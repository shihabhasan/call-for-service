from collections import Counter
from datetime import timedelta
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from django.db.models import Min, Max, Count, Case, When, IntegerField, F, Avg, \
    DurationField, StdDev, Q
from postgres_stats import Extract, DateTrunc, Percentile
from url_filter.filtersets import StrictMode
from .models import OfficerActivity, OfficerActivityType, Call, Beat, \
    NatureGroup
from .filters import CallFilterSet, OfficerActivityFilterSet


class Secs(Extract):
    name = 'secs'

    def __init__(self, expression, **extra):
        super().__init__(expression, subfield='EPOCH', **extra)


class OfficerActivityOverview:
    def __init__(self, filters):
        self._filters = filters
        self.filter = OfficerActivityFilterSet(data=filters,
                                               queryset=OfficerActivity.objects.all())
        self.bounds = self.qs.aggregate(min_time=Min('time'),
                                        max_time=Max('time'))

        # The interval between discrete time samples in the database
        # in secondes
        self.sample_interval = 10 * 60

    @property
    def qs(self):
        return self.filter.filter()

    def round_datetime(self, d, decimals=-1):
        """
        Round the given date time to the given decimal precision (defaults to 10 mins).

        Note that default Python3 rounding exhibits "round-toward-even" behavior:
        http://stackoverflow.com/questions/10825926/python-3-x-rounding-behavior

        This means that round(5, -1) = 0 and round(15, -1) = 20.
        """
        return d - timedelta(minutes=d.minute - round(d.minute, decimals),
                             seconds=d.second,
                             microseconds=d.microsecond)

    def allocation_over_time(self):
        # Return an empty list if we didn't get any data
        if (not self.bounds['max_time'] or not self.bounds['min_time']):
            return []

        activity_type_lookup = {r.officer_activity_type_id: r.descr
                                for r in OfficerActivityType.objects.all()
                                }

        # In order for this to show average allocation, we need to know the number
        # of times each time sample occurs.
        start = self.round_datetime(self.bounds['min_time'])
        end = self.round_datetime(self.bounds['max_time'])
        total_seconds = int((end - start).total_seconds())
        time_freq = Counter((start + timedelta(seconds=x)).time() for x in
                            range(0, total_seconds + 1, self.sample_interval))

        # We have to raise the work_mem for this query so the large
        # sort isn't performed on disk
        cursor = connection.cursor()
        cursor.execute('SET work_mem=\'30MB\';')

        # We have to strip off the date component by casting to time
        results = self.qs \
            .extra({'time_hour_minute': 'time_::time'}) \
            .values('time_hour_minute', 'activity_type') \
            .annotate(avg_volume=Count('*'))

        # Make sure we have an entry for each combination of time and
        # activity; go ahead and fill out the frequency (number of times
        # the given time sample occured).
        agg_result = {t: {
            'IN CALL - CITIZEN INITIATED': {
                'avg_volume': 0,
                'total': 0,
                'freq': time_freq[t]
            },
            'IN CALL - SELF INITIATED': {
                'avg_volume': 0,
                'total': 0,
                'freq': time_freq[t]
            },
            'IN CALL - DIRECTED PATROL': {
                'avg_volume': 0,
                'total': 0,
                'freq': time_freq[t]
            },
            'OUT OF SERVICE': {
                'avg_volume': 0,
                'total': 0,
                'freq': time_freq[t]
            },
            'ON DUTY': {
                'avg_volume': 0,
                'total': 0,
                'freq': time_freq[t]
            }
        } for t in time_freq}

        for r in results:
            time_ = r['time_hour_minute']
            activity = activity_type_lookup[r['activity_type']]
            freq = agg_result[time_][activity]['freq']
            agg_result[time_][activity]['total'] = r['avg_volume']
            agg_result[time_][activity]['avg_volume'] = r['avg_volume']
            try:
                agg_result[time_][activity]['avg_volume'] /= freq
            except ZeroDivisionError:
                agg_result[time_][activity]['avg_volume'] = 0

        # Set the work_mem back to normal
        cursor.execute('RESET work_mem;')
        cursor.close()

        # Patrol stats are ON DUTY minus everything else
        for r in agg_result.values():
            r['PATROL'] = {
                'freq': r['ON DUTY']['freq'],
                'total': r['ON DUTY']['total'] \
                         - sum(
                    [v['total'] for k, v in r.items() if not k == 'ON DUTY']),
                'avg_volume': r['ON DUTY']['avg_volume'] \
                              - sum([v['avg_volume'] for k, v in r.items() if
                                     not k == 'ON DUTY']),
            }

        # Keys have to be strings to transmit to the client
        return {str(k): v for k, v in agg_result.items()}

    def on_duty_by_beat(self):
        cursor = connection.cursor()

        cte_sql, params = self.qs.query.sql_with_params()

        sql = """
        WITH cur_doa AS (
          {cte_sql}
        )
        SELECT
          beat,
          beat_id,
          avg(count) AS on_duty
        FROM (
            SELECT
              b.descr AS beat,
              b.beat_id,
              date_trunc('minute', doa.time_) AS time_,
              count(*)
            FROM
              cur_doa doa
                INNER JOIN call_unit cu
                  ON (doa.call_unit_id = cu.call_unit_id)
                INNER JOIN beat b
                  ON (cu.beat_id = b.beat_id)
            WHERE
              doa.officer_activity_type_id = (
                  SELECT officer_activity_type_id
                  FROM officer_activity_type
                  WHERE descr = 'ON DUTY'
              )
            GROUP BY b.descr, b.beat_id, date_trunc('minute', doa.time_)
        ) a
        GROUP BY beat, beat_id;
        """.format(cte_sql=cte_sql)
    
        cursor.execute(sql, params)
        results = dictfetchall(cursor)

        return results

    def on_duty_by_district(self):
        cursor = connection.cursor()

        cte_sql, params = self.qs.query.sql_with_params()

        sql = """
        WITH cur_doa AS (
          {cte_sql}
        )
        SELECT
          district,
          district_id,
          avg(count) AS on_duty
        FROM (
            SELECT
              d.descr AS district,
              d.district_id,
              date_trunc('minute', doa.time_) AS time_,
              count(*)
            FROM
              cur_doa doa
                INNER JOIN call_unit cu
                  ON (doa.call_unit_id = cu.call_unit_id)
                INNER JOIN district d
                  ON (cu.district_id = d.district_id)
            WHERE
            doa.officer_activity_type_id = (
                SELECT officer_activity_type_id
                FROM officer_activity_type
                WHERE descr = 'ON DUTY'
            )
            GROUP BY d.descr, d.district_id, date_trunc('minute', doa.time_)
        ) a
        GROUP BY district, district_id;
        """.format(cte_sql=cte_sql)
    
        cursor.execute(sql, params)
        results = dictfetchall(cursor)
        return results

    def to_dict(self):
        return {
            'filter': self.filter.data,
            'bounds': self.bounds,
            'allocation_over_time': self.allocation_over_time(),
            'on_duty_by_beat': self.on_duty_by_beat(),
            'on_duty_by_district': self.on_duty_by_district(),
        }


class CallOverview:
    def __init__(self, filters):
        self._filters = filters
        print(filters)
        self.filter = CallFilterSet(data=filters, queryset=Call.objects.all(),
                                    strict_mode=StrictMode.fail)
        self.bounds = self.qs.aggregate(min_time=Min('time_received'),
                                        max_time=Max('time_received'))
        if self.bounds['max_time'] and self.bounds['min_time']:
            self.span = self.bounds['max_time'] - self.bounds['min_time']
        else:
            self.span = timedelta(0, 0)

    @property
    def qs(self):
        return self.filter.filter()

    def count(self):
        return self.qs.count()

    def beat_ids(self):
        return dict(Beat.objects.all().values_list('descr', 'beat_id'))


class CallVolumeOverview(CallOverview):
    def precision(self):
        if self.span >= timedelta(days=365):
            return 'month'
        elif self.span >= timedelta(days=7):
            return 'day'
        else:
            return 'hour'

    def volume_by_date(self):
        results = self.qs \
            .annotate(
            date=DateTrunc('time_received', precision=self.precision())) \
            .values("date") \
            .annotate(volume=Count("date")) \
            .order_by("date")

        return results

    def volume_by_source(self):
        results = self.qs \
            .annotate(id=Case(
            When(call_source__descr="Self Initiated", then=0),
            default=1,
            output_field=IntegerField())) \
            .values("id") \
            .annotate(volume=Count("id"))

        return self.merge_data(results, [0, 1])

    def merge_data(self, src_data, all_ids):
        src_data = list(src_data)
        all_ids = set(all_ids)
        present_ids = set(x['id'] for x in src_data)

        for id in all_ids.difference(present_ids):
            src_data.append({"id": id, "volume": 0})

        return src_data

    def volume_by_shift(self):
        results = self.qs \
            .annotate(id=Case(
            When(Q(hour_received__gte=6) & Q(hour_received__lt=18), then=0),
            default=1,
            output_field=IntegerField())) \
            .values("id") \
            .annotate(volume=Count("id"))

        return self.merge_data(results, [0, 1])

    def volume_by_dow(self):
        results = self.qs \
            .annotate(id=F('dow_received'), name=F('dow_received')) \
            .values("id", "name") \
            .annotate(volume=Count('name'))

        return self.merge_data(results, range(0, 7))

    def volume_by_field(self, field):
        field_model = getattr(self.qs.model, field).field.related_model
        all_in_field = field_model.objects.annotate(
            name=F("descr"),
            id=F(field + "_id")).values('name', 'id')
        qs = self.qs.annotate(name=F(field + "__descr"),
                              id=F(field + "_id")).values('name', 'id')
        qs = qs.annotate(volume=Count('name'))

        results = list(qs)

        present_ids = set(x['id'] for x in results)

        for row in all_in_field:
            if row['id'] not in present_ids:
                row.update({"volume": 0})
                results.append(row)

        return results

    def volume_by_nature_group(self):
        all_in_field = NatureGroup.objects.annotate(
            name=F("descr"),
            id=F("nature_group_id")).values('name', 'id')

        results = self.qs \
            .annotate(id=F("nature__nature_group_id"),
                      name=F("nature__nature_group__descr")) \
            .values("name", "id") \
            .annotate(volume=Count('name'))

        results = list(results)

        present_ids = set(x['id'] for x in results)

        for row in all_in_field:
            if row['id'] not in present_ids:
                row.update({"volume": 0})
                results.append(row)

        return results


    def to_dict(self):
        return {
            'filter': self.filter.data,
            'bounds': self.bounds,
            'precision': self.precision(),
            'count': self.count(),
            'volume_by_date': self.volume_by_date(),
            'volume_by_source': self.volume_by_source(),
            'volume_by_nature': self.volume_by_field('nature'),
            'volume_by_nature_group': self.volume_by_nature_group(),
            'volume_by_beat': self.volume_by_field('beat'),
            'volume_by_dow': self.volume_by_dow(),
            'volume_by_shift': self.volume_by_shift(),
            'beat_ids': self.beat_ids(),
        }


class CallResponseTimeOverview(CallOverview):
    def officer_response_time(self):
        results = self.qs.filter(
            officer_response_time__gt=timedelta(0)).aggregate(
            avg=Avg(Secs('officer_response_time')),
            quartiles=Percentile(Secs('officer_response_time'),
                                 [0.25, 0.5, 0.75],
                                 output_field=ArrayField(DurationField)),
            max=Max(Secs('officer_response_time')))

        quartiles = results['quartiles']

        if quartiles:
            return {
                'quartiles': quartiles,
                'avg': results['avg'],
                'max': results['max'],
                'iqr': quartiles[2] - quartiles[0]
            }
        else:
            return {}

    def officer_response_time_by_field(self, field):
        field_model = getattr(self.qs.model, field).field.related_model
        all_in_field = field_model.objects.annotate(
            name=F("descr"),
            id=F(field + "_id")).values('name', 'id')

        results = self.qs \
            .annotate(id=F(field + "_id"),
                      name=F(field + '__descr')) \
            .values("id", "name") \
            .exclude(id=None) \
            .annotate(mean=Avg(Secs("officer_response_time"))) \
            .order_by("-mean")

        results = list(results)
        present_ids = set(x['id'] for x in results)

        for row in all_in_field:
            if row['id'] not in present_ids:
                row.update({"mean": 0})
                results.append(row)

        return results

    def to_dict(self):
        return {
            'filter': self.filter.data,
            'bounds': self.bounds,
            'count': self.count(),
            'officer_response_time': self.officer_response_time(),
            'officer_response_time_by_source': self.officer_response_time_by_field(
                'call_source'),
            'officer_response_time_by_beat': self.officer_response_time_by_field(
                'beat'),
            'officer_response_time_by_priority': self.officer_response_time_by_field(
                'priority'),
            'beat_ids': self.beat_ids(),
        }


class MapOverview(CallOverview):
    def officer_response_time_by_beat(self):
        results = self.qs \
            .annotate(name=F("beat__descr")) \
            .values("name") \
            .exclude(name=None) \
            .annotate(mean=Avg(Secs("officer_response_time"))) \
            .order_by("-mean")
        return results

    def volume_by_beat(self):
        qs = self.qs \
            .annotate(name=F('beat__descr')) \
            .values('name') \
            .exclude(name=None)

        return qs.annotate(volume=Count('name'))

    def to_dict(self):
        return {
            'filter': self.filter.data,
            'count': self.count(),
            'officer_response_time': self.officer_response_time_by_beat(),
            'call_volume': self.volume_by_beat()
        }


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]
