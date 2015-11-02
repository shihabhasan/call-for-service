# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.

from __future__ import unicode_literals
from collections import Counter
from datetime import timedelta

from django.db import models, connection
from django.db.models import Count, Aggregate, DurationField, Min, Max, \
    IntegerField, Sum, Case, When, F
from django.db.models.expressions import Func
from django.http import QueryDict


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]


class DateTrunc(Func):
    """
    Truncates a timestamp. Useful for investigating time series.

    The `by` named parameter can take:

    * microseconds
    * milliseconds
    * second
    * minute
    * hour
    * day
    * week
    * month
    * quarter
    * year
    * decade
    * century
    * millennium
    """

    function = "DATE_TRUNC"
    template = "%(function)s('%(by)s', %(expressions)s)"

    def __init__(self, expression, **extra):
        self.expression = expression
        try:
            self.by = extra['by']
        except KeyError:
            raise ValueError("by named argument must be specified")
        super().__init__(expression, **extra)


class DurationAvg(Aggregate):
    function = 'AVG'
    name = 'Avg'
    template = "%(function)s(EXTRACT(EPOCH FROM %(expressions)s))"

    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=DurationField(), **extra)


class DurationStdDev(Aggregate):
    function = 'STDDEV_POP'
    name = 'StdDev'
    template = "%(function)s(EXTRACT(EPOCH FROM %(expressions)s))"

    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=DurationField(), **extra)


class CallOverview:
    def __init__(self, filters):
        self._filters = filters
        from .filters import CallFilterSet
        self.filter = CallFilterSet(data=filters, queryset=Call.objects.all())
        self.bounds = self.qs.aggregate(min_time=Min('time_received'),
                                        max_time=Max('time_received'))
        if self.bounds['max_time'] and self.bounds['min_time']:
            self.span = self.bounds['max_time'] - self.bounds['min_time']
        else:
            self.span = timedelta(0, 0)

    @property
    def qs(self):
        return self.filter.filter()

    def officer_response_time(self):
        results = self.qs.aggregate(avg=DurationAvg('officer_response_time'),
                                    stddev=DurationStdDev('officer_response_time'))
        return {
            'avg': results['avg'],
            'stddev': results['stddev']
        }

    def volume_by_date(self):
        cursor = connection.cursor()

        cte_sql, params = self.qs. \
            annotate(date=DateTrunc('time_received', by='day')). \
            values('date'). \
            annotate(volume=Count('date')).query.sql_with_params()
        sql = """
        WITH daily_stats AS (
            {cte_sql}
        )
        SELECT
            ds1.date AS date,
            ds1.volume AS volume,
            CAST(AVG(ds2.volume) AS INTEGER) AS average
        FROM daily_stats AS ds1
        JOIN daily_stats AS ds2
            ON ds2.date BETWEEN ds1.date - INTERVAL '15 days' AND
            ds1.date + INTERVAL '15 days'
        GROUP BY ds1.date, ds1.volume
        ORDER BY ds1.date;
        """.format(cte_sql=cte_sql)

        cursor.execute(sql, params)
        results = dictfetchall(cursor)
        return results

    def day_hour_heatmap(self):
        if self.span == timedelta(0, 0):
            return []

        # In order for this to show average volume, we need to know the number 
        # of times each day of the week occurs.
        start = self.bounds['min_time'].date()
        end = self.bounds['max_time'].date()
        weekdays = Counter((start + timedelta(days=x)).weekday() for x in
                           range(0, (end - start).days + 1))

        results = self.qs \
            .values('dow_received', 'hour_received') \
            .annotate(volume=Count('dow_received')) \
            .order_by('dow_received', 'hour_received')

        for result in results:
            result['freq'] = weekdays[result['dow_received']]
            result['total'] = result['volume']
            try:
                result['volume'] /= result['freq']
            except ZeroDivisionError:
                result['volume'] = 0

        return results

    def volume_by_source(self):
        results = self.qs \
            .annotate(date=DateTrunc('time_received', by='day'),
                      self_initiated=Case(
                          When(call_source__descr="Self Initiated", then=True),
                          default=False,
                          output_field=IntegerField())) \
            .values("date", "self_initiated") \
            .annotate(volume=Count("self_initiated")) \
            .order_by("date")

        return results

    def officer_response_time_by_beat(self):
        results = self.qs \
            .values("beat", "beat__descr") \
            .annotate(mean=DurationAvg("officer_response_time"),
                      stddev=DurationStdDev("officer_response_time"),
                      missing=Sum(Case(When(officer_response_time=None, then=1),
                                       default=0,
                                       output_field=IntegerField())))
        return results

    def officer_response_time_by_source(self):
        results = self.qs \
            .annotate(id=F('call_source'),
                      name=F('call_source__descr')) \
            .values("id", "name") \
            .exclude(id=None) \
            .annotate(mean=DurationAvg("officer_response_time")) \
            .order_by("-mean")
        return results

    def volume_by_beat(self):
        qs = self.qs.annotate(name=F('beat__descr'), id=F('beat_id')).values(
            'name', 'id')
        return qs.annotate(volume=Count('name'))

    def volume_by_field(self, field):
        qs = self.qs.annotate(name=F(field + "__descr"),
                              id=F(field + "_id")).values('name', 'id')
        return qs.annotate(volume=Count('name'))

    def to_dict(self):
        return {
            'filter': self.filter.data,
            'bounds': self.bounds,
            'volume_by_date': self.volume_by_date(),
            'day_hour_heatmap': self.day_hour_heatmap(),
            'volume_by_source': self.volume_by_source(),
            'volume_by_nature': self.volume_by_field('nature'),
            'volume_by_beat': self.volume_by_field('beat'),
            'officer_response_time_by_source': self.officer_response_time_by_source(),
            # 'volume_by_close_code': self.volume_by_field('close_code'),
            # 'officer_response_time_by_beat': self.officer_response_time_by_beat()
            # 'officer_response_time': self.officer_response_time()
        }


class ModelWithDescr(models.Model):
    descr = models.TextField("Description", blank=False, null=False)

    def __str__(self):
        if self.descr:
            return self.descr
        else:
            return super().__str__()

    class Meta:
        abstract = True
        ordering = ['descr']


class Sector(ModelWithDescr):
    sector_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'sector'


class District(ModelWithDescr):
    district_id = models.IntegerField(primary_key=True)
    sector = models.ForeignKey(Sector, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'district'


class Beat(ModelWithDescr):
    beat_id = models.IntegerField(primary_key=True)
    district = models.ForeignKey(District, blank=True, null=True)
    sector = models.ForeignKey(Sector, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'beat'


class CallSource(ModelWithDescr):
    call_source_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'call_source'


class City(ModelWithDescr):
    city_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'city'


class Squad(ModelWithDescr):
    squad_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'squad'


class CallUnit(ModelWithDescr):
    call_unit_id = models.IntegerField(primary_key=True)
    squad = models.ForeignKey(Squad, blank=True, null=True,
                              db_column="squad_id",
                              related_name="squad")

    class Meta:
        managed = False
        db_table = 'call_unit'


class Nature(ModelWithDescr):
    nature_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'nature'


class CloseCode(ModelWithDescr):
    close_code_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'close_code'


class OOSCode(ModelWithDescr):
    oos_code_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'oos_code'


class OutOfServicePeriod(models.Model):
    oos_id = models.IntegerField(primary_key=True)
    call_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                  db_column="call_unit_id",
                                  related_name="+")
    shift_unit_id = models.BigIntegerField(blank=True, null=True)
    oos_code = models.ForeignKey(OOSCode, blank=True, null=True,
                                 db_column="oos_code_id",
                                 related_name="+")
    location = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'out_of_service'

class Shift(models.Model):
    shift_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'shift'

class Officer(models.Model):
    officer_id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    name_aka = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'officer'

class Bureau(ModelWithDescr):
    bureau_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'bureau'

class Division(ModelWithDescr):
    division_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'division'

class Unit(ModelWithDescr):
    unit_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'unit'


class ShiftUnit(models.Model):
    shift_unit_id = models.IntegerField(primary_key=True)
    call_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                  db_column="call_unit_id",
                                  related_name="+")
    officer = models.ForeignKey(Officer, blank=True, null=True,
                                db_column="officer_id",
                                related_name="+")
    in_time = models.DateTimeField(blank=True, null=True)
    out_time = models.DateTimeField(blank=True, null=True)
    bureau = models.ForeignKey(Bureau, blank=True, null=True,
                               db_column="bureau_id",
                               related_name="+")
    division = models.ForeignKey(Division, blank=True, null=True,
                               db_column="division_id",
                               related_name="+")
    unit = models.ForeignKey(Unit, blank=True, null=True,
                               db_column="unit_id",
                               related_name="+")
    shift = models.ForeignKey(Shift, blank=True, null=True,
                              db_column="shift_id",
                              related_name="+")

    class Meta:
        managed = False
        db_table = 'shift_unit'



# Primary Classes

class Call(models.Model):
    call_id = models.BigIntegerField(primary_key=True)
    year_received = models.IntegerField(blank=True, null=True)
    month_received = models.IntegerField(blank=True, null=True)
    week_received = models.IntegerField(blank=True, null=True)
    dow_received = models.IntegerField(blank=True, null=True)
    hour_received = models.IntegerField(blank=True, null=True)
    case_id = models.BigIntegerField(blank=True, null=True)
    call_source = models.ForeignKey('CallSource', blank=True, null=True)
    primary_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                     related_name="+")
    first_dispatched = models.ForeignKey(CallUnit, blank=True, null=True,
                                         related_name="+")
    reporting_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                       related_name="+")
    street_num = models.IntegerField(blank=True, null=True)
    street_name = models.TextField(blank=True, null=True)
    city = models.ForeignKey('City', blank=True, null=True)
    zip_code = models.ForeignKey('ZipCode', blank=True, null=True)
    crossroad1 = models.TextField(blank=True, null=True)
    crossroad2 = models.TextField(blank=True, null=True)
    geox = models.FloatField(blank=True, null=True)
    geoy = models.FloatField(blank=True, null=True)
    beat = models.ForeignKey(Beat, blank=True, null=True, related_name='+')
    district = models.ForeignKey('District', blank=True, null=True, related_name='+')
    sector = models.ForeignKey('Sector', blank=True, null=True, related_name='+')
    business = models.TextField(blank=True, null=True)
    nature = models.ForeignKey('Nature', blank=True, null=True)
    priority = models.ForeignKey('Priority', blank=True, null=True)
    report_only = models.NullBooleanField()
    cancelled = models.NullBooleanField()
    time_received = models.DateTimeField(blank=True, null=True)
    time_routed = models.DateTimeField(blank=True, null=True)
    time_finished = models.DateTimeField(blank=True, null=True)
    first_unit_dispatch = models.DateTimeField(blank=True, null=True)
    first_unit_enroute = models.DateTimeField(blank=True, null=True)
    first_unit_arrive = models.DateTimeField(blank=True, null=True)
    first_unit_transport = models.DateTimeField(blank=True, null=True)
    last_unit_clear = models.DateTimeField(blank=True, null=True)
    time_closed = models.DateTimeField(blank=True, null=True)
    close_code = models.ForeignKey('CloseCode', blank=True, null=True)
    close_comments = models.TextField(blank=True, null=True)
    incident = models.ForeignKey('Incident', blank=True, null=True)
    officer_response_time = models.DurationField(blank=True, null=True)
    overall_response_time = models.DurationField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'call'

class InCallPeriod(models.Model):
    in_call_id = models.IntegerField(primary_key=True)
    call_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                  db_column="call_unit_id",
                                  related_name="+")
    shift = models.ForeignKey(Shift, blank=True, null=True,
                              db_column="shift_id",
                              related_name="+")
    call = models.ForeignKey(Call, blank=True, null=True,
                             db_column="call_id",
                             related_name="+")
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'in_call'



class Incident(models.Model):
    incident_id = models.BigIntegerField(primary_key=True)
    case_id = models.BigIntegerField(unique=True, blank=True, null=True)
    time_filed = models.DateTimeField(blank=True, null=True)
    month_filed = models.IntegerField(blank=True, null=True)
    week_filed = models.IntegerField(blank=True, null=True)
    dow_filed = models.IntegerField(blank=True, null=True)
    street_num = models.IntegerField(blank=True, null=True)
    street_name = models.TextField(blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True)
    # zip_code = models.ForeignKey('ZipCode', blank=True, null=True)
    # zipcode     = models.IntegerField(blank=True, null=True, db_column="zip")
    geox = models.FloatField(blank=True, null=True)
    geoy = models.FloatField(blank=True, null=True)
    beat = models.ForeignKey(Beat, blank=True, null=True)
    district = models.ForeignKey(District, blank=True, null=True)
    sector = models.ForeignKey(Sector, blank=True, null=True)
    # premise    = models.ForeignKey('Premise', blank=True, null=True)
    # weapon     = models.ForeignKey('Weapon', blank=True, null=True)
    domestic = models.NullBooleanField()
    juvenile = models.NullBooleanField()
    gang_related = models.NullBooleanField()
    # emp_bureau = models.ForeignKey(Bureau, blank=True, null=True)
    # emp_division = models.ForeignKey(Division, blank=True, null=True)
    # emp_unit = models.ForeignKey('Unit', blank=True, null=True)
    num_officers = models.IntegerField(blank=True, null=True)
    # investigation_status = models.ForeignKey('InvestigationStatus', blank=True, null=True)
    # investigator_unit = models.ForeignKey('Unit', blank=True, null=True)
    # case_status = models.ForeignKey(CaseStatus, blank=True, null=True)
    # ucr_code = models.IntegerField(blank=True, null=True)
    # ucr_descr = models.ForeignKey('UcrDescr', blank=True, null=True)
    committed = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'incident'


class Priority(ModelWithDescr):
    priority_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'priority'


class ZipCode(ModelWithDescr):
    zip_code_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'zip_code'
