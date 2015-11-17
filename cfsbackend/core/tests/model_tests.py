from dateutil.parser import parse as dtparse
from django.http import QueryDict
from django.test import TestCase
from .test_helpers import assert_list_equiv

from ..models import Call, Beat, Secs, CallVolumeOverview, \
        CallUnit, OfficerActivity, OfficerActivityOverview, Nature
from datetime import timedelta


def create_call(**kwargs):
    try:
        time_received = dtparse(kwargs['time_received'])
    except KeyError:
        raise ValueError("You must include a time_received value.")

    kwargs['dow_received'] = time_received.weekday()
    kwargs['hour_received'] = time_received.hour

    return Call.objects.create(**kwargs)


def q(string):
    return QueryDict(string)

class OfficerActivityOverviewTest(TestCase):
    def setUp(self):
        n1 = Nature.objects.create(nature_id=1, descr='Robbery')
        n2 = Nature.objects.create(nature_id=2, descr='Homicide')
        call1 = create_call(call_id=1, time_received='2014-01-15T9:00',
                            nature=n1)
        call2 = create_call(call_id=2, time_received='2014-03-18T3:00',
                            nature=n2)
        cu1 = CallUnit.objects.create(call_unit_id=1, descr='A1')
        cu2 = CallUnit.objects.create(call_unit_id=2, descr='B2')
        a1 = OfficerActivity.objects.create(officer_activity_id=1,
                activity="IN CALL",
                time=dtparse('2014-01-15T9:00'),
                call_unit=cu1,
                call=call1)
        a2 = OfficerActivity.objects.create(officer_activity_id=2,
                activity="IN CALL",
                time=dtparse('2014-01-15T9:10'),
                call_unit=cu2,
                call=call1)
        a3 = OfficerActivity.objects.create(officer_activity_id=3,
                activity="IN CALL",
                time=dtparse('2014-01-15T10:00'),
                call_unit=cu1,
                call=call2)
        a4 = OfficerActivity.objects.create(officer_activity_id=4,
                activity="IN CALL",
                time=dtparse('2014-01-16T9:50'),
                call_unit=cu2,
                call=call2)
        a5 = OfficerActivity.objects.create(officer_activity_id=5,
                activity="OUT OF SERVICE",
                time=dtparse('2014-01-16T10:10'),
                call_unit=cu1,
                call=None)
        a6 = OfficerActivity.objects.create(officer_activity_id=6,
                activity="OUT OF SERVICE",
                time=dtparse('2014-01-18T9:00'),
                call_unit=cu2,
                call=None)

    def test_distinguishes_activities(self):
        "Make sure we pick up on there being two types of activities."
        overview = OfficerActivityOverview(q(''))
        results = overview.to_dict()['allocation_over_time']
        
        self.assertEqual(sorted(set([r['activity'] for r in results])),
                ['IN CALL', 'OUT OF SERVICE'])
        
    def test_evaluates_no_activity(self):
        # Should return 0 activities
        overview = OfficerActivityOverview(q('time__gte=2015-01-01'))
        results = overview.to_dict()['allocation_over_time']

        self.assertEqual(results, [])

    def test_evaluates_one_activity(self):
        # Should return 1 activity (a6)
        overview = OfficerActivityOverview(q('time__gte=2014-01-17'))
        results = overview.to_dict()['allocation_over_time']

        correct_results = [{
            'activity': 'OUT OF SERVICE',
            'time_hour_minute': dtparse('9:00').time(),
            'freq': 1,
            'total': 1,
            'avg_volume': 1.0
        }]


        self.assertEqual(sorted(results, key=lambda x: x['time_hour_minute']), correct_results)

    # The concept of overlapping activities is deprecated since we're applying
    # the conversion from continuous intervals to discrete time points in the
    # database now.  It doesn't hurt to have these (modified) test cases in here,
    # though.

    def test_evaluates_two_nonoverlapping_activities(self):
        # Should return 2 activities (a5, a6) that don't overlap in the
        # same time period
        overview = OfficerActivityOverview(q('activity=OUT+OF+SERVICE'))
        results = overview.to_dict()['allocation_over_time']
        
        correct_results = [{
            'activity': 'OUT OF SERVICE',
            'time_hour_minute': dtparse('9:00').time(),
            'freq': 2,
            'total': 1,
            'avg_volume': 0.5
        }, {
            'activity': 'OUT OF SERVICE',
            'time_hour_minute': dtparse('10:10').time(),
            'freq': 2,
            'total': 1,
            'avg_volume': 0.5
        }]

        self.assertEqual(sorted(results, key=lambda x: x['time_hour_minute']), correct_results)

    def test_evaluates_two_overlapping_activities(self):
        # Should return 2 activities (a1, a2) that overlap in the same time period
        overview = OfficerActivityOverview(q('call__nature=1'))
        results = overview.to_dict()['allocation_over_time']
        
        correct_results = [{
            'activity': 'IN CALL',
            'time_hour_minute': dtparse('9:00').time(),
            'freq': 1,
            'total': 1,
            'avg_volume': 1.0
        }, {
            'activity': 'IN CALL',
            'time_hour_minute': dtparse('9:10').time(),
            'freq': 1,
            'total': 1,
            'avg_volume': 1.0
        }]

        self.assertEqual(sorted(results, key=lambda x: x['time_hour_minute']), correct_results)


class CallVolumeOverviewTest(TestCase):
    def setUp(self):
        b1 = Beat.objects.create(beat_id=1, descr="B1")
        b2 = Beat.objects.create(beat_id=2, descr="B2")
        create_call(call_id=1, time_received='2014-01-15T09:00',
                    officer_response_time=timedelta(0, 120),
                    beat=b1)
        create_call(call_id=2, time_received='2015-01-01T09:00',
                    officer_response_time=timedelta(0, 600),
                    beat=b1)
        create_call(call_id=3, time_received='2015-01-01T12:30',
                    officer_response_time=timedelta(0, 900),
                    beat=b2)
        create_call(call_id=4, time_received='2015-01-08T09:00',
                    beat=b1)
        create_call(call_id=5, time_received='2015-02-01T09:00',
                    beat=b2)
        create_call(call_id=6, time_received='2014-11-01T12:00',
                    beat=b1)

    def test_moving_average(self):
        overview = CallVolumeOverview(q(''))
        results = overview.to_dict()['volume_by_date']

        correct_items = [
            {"date": dtparse("2014-01-15"),
             "volume": 1, "average": 1},
            {"date": dtparse("2014-11-01"),
             "volume": 1, "average": 1},

            # Correct avg is 2 instead of 1.5 because
            # postgres' int cast rounds 1.5 up
            {"date": dtparse("2015-01-01"),
             "volume": 2, "average": 2},
            {"date": dtparse("2015-01-08"),
             "volume": 1, "average": 2},
            {"date": dtparse("2015-02-01"),
             "volume": 1, "average": 1}]

        # There's probably a better way to do this,
        # but this works; the order of the results is
        # irrelevant, but we can't make a set out of them
        # because dicts aren't hashable.

        for res in results:
            self.assertIn(res, correct_items)

        for item in correct_items:
            self.assertIn(item, results)

    # These tests aren't relevant with the replacement of volume_over_time by
    # volume_by_date, but we may need them if we decide to scale volume_by_date
    # automatically again
    def test_call_volume_for_day(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2015-01-01&time_received__lte=2015-01-02"))
        assert overview.bounds == {"min_time": dtparse("2015-01-01T09:00"),
                                   "max_time": dtparse('2015-01-01T12:30')}

        assert_list_equiv(overview.volume_by_date(),
                          [{"date": dtparse("2015-01-01T00:00"), "volume": 2,
                            "average": 2}])

    def test_call_volume_for_multiple_days(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2015-01-01&time_received__lte=2015-01-09"))
        results = overview.volume_by_date()
        assert overview.bounds == {"min_time": dtparse("2015-01-01T09:00"),
                                   "max_time": dtparse('2015-01-08T09:00')}

        assert_list_equiv(results,
                          [{"date": dtparse("2015-01-01T00:00"), "volume": 2,
                            "average": 2},
                           {"date": dtparse("2015-01-08T00:00"), "volume": 1,
                            "average": 2}])

    def test_call_volume_for_month(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2015-01-01&time_received__lte=2015-02-02"))
        results = overview.volume_by_date()
        assert overview.bounds == {"min_time": dtparse("2015-01-01T09:00"),
                                   "max_time": dtparse('2015-02-01T09:00')}
        assert_list_equiv(results,
                          [{"date": dtparse("2015-01-01T00:00"), "volume": 2,
                            'average': 2},
                           {"date": dtparse("2015-01-08T00:00"), "volume": 1,
                            'average': 2},
                           {"date": dtparse("2015-02-01T00:00"), "volume": 1,
                            'average': 1}])

    def test_call_volume_for_multiple_months(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2014-11-01&time_received__lte=2015-02-02"))
        results = overview.volume_by_date()
        assert overview.bounds == {"min_time": dtparse("2014-11-01T12:00"),
                                   "max_time": dtparse('2015-02-01T09:00')}

        assert_list_equiv(results,
                          [{"date": dtparse("2014-11-01"), "volume": 1,
                            "average": 1},
                           {"date": dtparse("2015-01-01"), "volume": 2,
                            "average": 2},
                           {"date": dtparse("2015-01-08"), "volume": 1,
                            "average": 2},
                           {"date": dtparse("2015-02-01"), "volume": 1,
                            "average": 1}])

    def test_call_volume_for_year(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2014-01-01&time_received__lte=2015-02-02"))
        results = overview.volume_by_date()
        assert overview.bounds == {"min_time": dtparse("2014-01-15T09:00"),
                                   "max_time": dtparse('2015-02-01T09:00')}

        assert_list_equiv(results,
                          [{"date": dtparse("2014-01-15T00:00"), "volume": 1,
                            "average": 1},
                           {"date": dtparse("2014-11-01T00:00"), "volume": 1,
                            "average": 1},
                           {"date": dtparse("2015-01-01T00:00"), "volume": 2,
                            "average": 2},
                           {"date": dtparse("2015-01-08T00:00"), "volume": 1,
                            "average": 2},
                           {"date": dtparse("2015-02-01T00:00"), "volume": 1,
                            "average": 1}])

    def test_day_hour_heatmap(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2015-01-01&time_received__lte=2015-02-02"))
        results = overview.to_dict()['day_hour_heatmap']

        assert_list_equiv(results, [
            {'dow_received': 3, 'hour_received': 9, 'volume': 0.4, 'freq': 5,
             'total': 2},
            {'dow_received': 3, 'hour_received': 12, 'volume': 0.2, 'freq': 5,
             'total': 1},
            {'dow_received': 6, 'hour_received': 9, 'volume': 0.2, 'freq': 5,
             'total': 1},
        ])
