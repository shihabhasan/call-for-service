from collections import Counter
from datetime import timedelta

from django.db import connection
from django.db.models import Min, Max, Count

from officer_allocation.filters import OfficerActivityFilterSet
from officer_allocation.models import OfficerActivity, OfficerActivityType


class OfficerActivityOverview:
    def __init__(self, filters):
        self._filters = filters
        self.filter = OfficerActivityFilterSet(
            data=filters,
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
        Round the given date time to the given decimal precision (defaults to
        10 mins).

        Note that default Python3 rounding exhibits "round-toward-even"
        behavior:
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

        # In order for this to show average allocation, we need to know the
        # number of times each time sample occurs.
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
                'total': r['ON DUTY']['total'] - sum(
                    [v['total'] for k, v in r.items() if
                     not k == 'ON DUTY']),
                'avg_volume': r['ON DUTY']['avg_volume'] - sum(
                    [v['avg_volume'] for k, v in r.items() if
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

        # Band-aid fix for slow query; runs for almost
        # a minute when planner chooses a merge join.
        # Need to find out what's causing it.
        cursor.execute("SET enable_mergejoin=0;")
        cursor.execute(sql, params)
        results = dictfetchall(cursor)
        cursor.execute("RESET enable_mergejoin;")

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
            # Not using these on the front-end anymore
            # 'on_duty_by_beat': self.on_duty_by_beat(),
            # 'on_duty_by_district': self.on_duty_by_district(),
        }


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]
