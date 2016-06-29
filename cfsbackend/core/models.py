# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.

from django.db import models
from django.db.models import Q
from pg.view import MaterializedView
from django.contrib.postgres.fields import ArrayField
from solo.models import SingletonModel
from adminsortable.models import SortableMixin
from geoposition.fields import GeopositionField


class SiteConfiguration(SingletonModel):
    maintenance_mode = models.BooleanField(default=False)

    # Department
    department_name = models.CharField(max_length=255,
                                       default="City Police Department")
    department_abbr = models.CharField("Department abbreviation", max_length=10,
                                       default="CPD")

    # Features
    use_shift = models.BooleanField("Use shift?", default=False)
    use_district = models.BooleanField("Use district?", default=False)
    use_beat = models.BooleanField("Use beat?", default=False)
    use_squad = models.BooleanField("Use squad?", default=False)
    use_priority = models.BooleanField("Use priority?", default=False)
    use_nature = models.BooleanField("Use natures?", default=False)
    use_nature_group = models.BooleanField("Use nature groups?", default=False)
    use_call_source = models.BooleanField("Use call sources?", default=False)
    use_cancelled = models.BooleanField("Use cancelled?", default=False)

    # Geography
    geo_center = GeopositionField("Center", blank=True)
    geo_ne_bound = GeopositionField("Northeast bound", blank=True)
    geo_sw_bound = GeopositionField("Southwest bound", blank=True)
    geo_default_zoom = models.PositiveIntegerField("Default zoom level", default=11)
    geojson_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "* Site Configuration"


class DateTimeNoTZField(models.DateTimeField):
    """
    Django automatically creates datetime fields as timestamp with
    time zone; however, we've been creating them as no timezone.
    We need this to be consistent so any time shifts are applied
    uniformly across timestamp columns.
    """

    def db_type(self, connection):
        return 'timestamp without time zone'


def update_materialized_views():
    for view_cls in MaterializedView.__subclasses__():
        view_cls.update_view()


class ModelWithDescr(models.Model):
    descr = models.TextField("Description", unique=True)

    def __str__(self):
        if self.descr:
            return self.descr
        else:
            return super().__str__()

    class Meta:
        abstract = True
        ordering = ['descr']


class Beat(ModelWithDescr):
    beat_id = models.AutoField(primary_key=True)
    district = models.ForeignKey('District', blank=True, null=True)
    sector = models.ForeignKey('Sector', blank=True, null=True)

    class Meta:
        db_table = 'beat'


class Bureau(ModelWithDescr):
    bureau_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'bureau'


class CallQuerySet(models.QuerySet):
    def squad(self, value):
        if value:
            query = Q(primary_unit__squad_id=value) | Q(
                first_dispatched__squad_id=value) | Q(
                reporting_unit__squad_id=value)
            return self.filter(query)
        else:
            return self

    def unit(self, value):
        if value:
            query = Q(primary_unit_id=value) | Q(
                first_dispatched_id=value) | Q(
                reporting_unit_id=value)
            return self.filter(query)
        else:
            return self

    def initiated_by(self, value):
        if str(value) == "0":
            return self.filter(
                call_source=CallSource.objects.get(descr="Self Initiated"))
        elif str(value) == "1":
            return self.exclude(
                call_source=CallSource.objects.get(descr="Self Initiated"))
        else:
            return self

    def shift(self, value):
        if str(value) == "0":
            query = Q(hour_received__gte=6) & Q(hour_received__lt=18)
            return self.filter(query)
        elif str(value) == "1":
            query = Q(hour_received__lt=6) | Q(hour_received__gte=18)
            return self.filter(query)
        else:
            return self


class Call(models.Model):
    objects = CallQuerySet.as_manager()

    call_id = models.CharField(max_length=64, primary_key=True)
    time_received = DateTimeNoTZField(db_index=True)
    time_routed = DateTimeNoTZField(blank=True, null=True)
    time_finished = DateTimeNoTZField(blank=True, null=True)
    year_received = models.IntegerField(db_index=True)
    month_received = models.IntegerField(db_index=True)
    week_received = models.IntegerField(db_index=True)
    dow_received = models.IntegerField(db_index=True)
    hour_received = models.IntegerField(db_index=True)
    case_id = models.BigIntegerField(blank=True, null=True)
    call_source = models.ForeignKey('CallSource', blank=True, null=True)
    primary_unit = models.ForeignKey('CallUnit', blank=True, null=True,
                                     related_name="+")
    first_dispatched = models.ForeignKey('CallUnit', blank=True, null=True,
                                         related_name="+")
    reporting_unit = models.ForeignKey('CallUnit', blank=True, null=True,
                                       related_name="+")
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.ForeignKey('City', blank=True, null=True)
    zip_code = models.CharField(max_length=5, blank=True, null=True)
    crossroad1 = models.TextField(blank=True, null=True)
    crossroad2 = models.TextField(blank=True, null=True)
    geox = models.FloatField(blank=True, null=True)
    geoy = models.FloatField(blank=True, null=True)
    beat = models.ForeignKey(Beat, blank=True, null=True)
    district = models.ForeignKey('District', blank=True, null=True)
    sector = models.ForeignKey('Sector', blank=True, null=True)
    business = models.TextField(blank=True, null=True)
    nature = models.ForeignKey('Nature', blank=True, null=True)
    priority = models.ForeignKey('Priority', blank=True, null=True)
    report_only = models.BooleanField(default=False)
    cancelled = models.BooleanField(db_index=True, default=False)

    first_unit_dispatch = DateTimeNoTZField(blank=True, null=True)
    first_unit_enroute = DateTimeNoTZField(blank=True, null=True)
    first_unit_arrive = DateTimeNoTZField(blank=True, null=True)
    first_unit_transport = DateTimeNoTZField(blank=True, null=True)
    last_unit_clear = DateTimeNoTZField(blank=True, null=True)
    time_closed = DateTimeNoTZField(blank=True, null=True)
    close_code = models.ForeignKey('CloseCode', blank=True, null=True)
    close_comments = models.TextField(blank=True, null=True)
    officer_response_time = models.DurationField(blank=True, null=True,
                                                 db_index=True)
    overall_response_time = models.DurationField(blank=True, null=True)

    def update_derived_fields(self):
        self.month_received = self.time_received.month
        self.hour_received = self.time_received.hour
        self.year_received, self.week_received, _ = \
            self.time_received.isocalendar()
        self.dow_received = self.time_received.weekday()

        if self.first_unit_arrive is not None and self.time_received is not None:
            self.overall_response_time = self.first_unit_arrive - self.time_received

        if self.first_unit_arrive is not None and self.first_unit_dispatch is not None:
            self.officer_response_time = self.first_unit_arrive - self.first_unit_dispatch

    class Meta:
        db_table = 'call'
        index_together = [
            ['dow_received', 'hour_received']
        ]


class CallLog(models.Model):
    call_log_id = models.AutoField(primary_key=True)
    call = models.ForeignKey('Call', blank=True, null=True)
    transaction = models.ForeignKey('Transaction', blank=True, null=True)
    shift = models.ForeignKey('Shift', blank=True, null=True)
    time_recorded = DateTimeNoTZField(blank=True, null=True)
    call_unit = models.ForeignKey('CallUnit', blank=True, null=True)
    close_code = models.ForeignKey('CloseCode', blank=True, null=True)

    class Meta:
        db_table = 'call_log'


class CallSource(ModelWithDescr):
    call_source_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'call_source'


class CallUnit(ModelWithDescr):
    call_unit_id = models.AutoField(primary_key=True)
    squad = models.ForeignKey('Squad', blank=True, null=True,
                              related_name="squad")
    beat = models.ForeignKey("Beat", blank=True, null=True, related_name="+")
    district = models.ForeignKey("District", blank=True, null=True,
                                 related_name="+")

    class Meta:
        db_table = 'call_unit'


class City(ModelWithDescr):
    city_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'city'
        verbose_name_plural = "cities"


class CloseCode(ModelWithDescr):
    close_code_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'close_code'


class District(ModelWithDescr):
    district_id = models.AutoField(primary_key=True)
    sector = models.ForeignKey('Sector', blank=True, null=True)

    class Meta:
        db_table = 'district'


class Division(ModelWithDescr):
    division_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'division'


class Sector(ModelWithDescr):
    sector_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'sector'


class Nature(ModelWithDescr):
    nature_id = models.AutoField(primary_key=True)
    nature_group = models.ForeignKey('NatureGroup', blank=True, null=True)
    key = models.CharField(max_length=10, blank=True, null=True, unique=True)

    class Meta:
        db_table = 'nature'


class NatureGroup(ModelWithDescr):
    nature_group_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'nature_group'


class Officer(models.Model):
    officer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    name_aka = ArrayField(models.CharField(max_length=255), blank=True)

    class Meta:
        db_table = 'officer'


class Priority(ModelWithDescr, SortableMixin):
    priority_id = models.AutoField(primary_key=True)
    sort_order = models.PositiveIntegerField(editable=False, db_index=True,
                                             default=0)

    class Meta:
        ordering = ('sort_order',)
        db_table = 'priority'
        verbose_name_plural = "priorities"


class Shift(models.Model):
    shift_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'shift'


class ShiftUnit(models.Model):
    shift_unit_id = models.AutoField(primary_key=True)
    call_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                  db_column="call_unit_id",
                                  related_name="+")
    officer = models.ForeignKey(Officer, blank=True, null=True,
                                db_column="officer_id",
                                related_name="+")
    in_time = DateTimeNoTZField(blank=True, null=True)
    out_time = DateTimeNoTZField(blank=True, null=True)
    bureau = models.ForeignKey(Bureau, blank=True, null=True,
                               db_column="bureau_id",
                               related_name="+")
    division = models.ForeignKey(Division, blank=True, null=True,
                                 db_column="division_id",
                                 related_name="+")
    unit = models.ForeignKey('Unit', blank=True, null=True,
                             db_column="unit_id",
                             related_name="+")
    shift = models.ForeignKey(Shift, blank=True, null=True,
                              db_column="shift_id",
                              related_name="+")

    class Meta:
        db_table = 'shift_unit'


class Squad(ModelWithDescr):
    squad_id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'squad'


class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    descr = models.TextField("Description", blank=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'transaction'
        ordering = ['code']


class Unit(ModelWithDescr):
    unit_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'unit'
