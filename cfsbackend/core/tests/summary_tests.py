from datetime import timedelta
from django.test import TestCase
from django.db.models import Model
from dateutil.parser import parse as dtparse
from core.summaries import OfficerActivityOverview, CallVolumeOverview
from .test_helpers import assert_list_equiv, create_call, q
from ..models import Beat, CallUnit, OfficerActivity, Nature, \
    OfficerActivityType


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
        at1 = OfficerActivityType.objects.create(
            officer_activity_type_id=1,
            descr="IN CALL - CITIZEN INITIATED")
        at2 = OfficerActivityType.objects.create(
            officer_activity_type_id=2,
            descr="OUT OF SERVICE")
        at3 = OfficerActivityType.objects.create(
            officer_activity_type_id=3,
            descr="ON DUTY")
        a1 = OfficerActivity.objects.create(officer_activity_id=1,
                                            activity_type=at1,
                                            time=dtparse('2014-01-15T9:00'),
                                            call_unit=cu1,
                                            call=call1)
        a2 = OfficerActivity.objects.create(officer_activity_id=2,
                                            activity_type=at1,
                                            time=dtparse('2014-01-15T9:10'),
                                            call_unit=cu2,
                                            call=call1)
        a3 = OfficerActivity.objects.create(officer_activity_id=3,
                                            activity_type=at1,
                                            time=dtparse('2014-01-15T10:00'),
                                            call_unit=cu1,
                                            call=call2)
        a4 = OfficerActivity.objects.create(officer_activity_id=4,
                                            activity_type=at1,
                                            time=dtparse('2014-01-16T9:50'),
                                            call_unit=cu2,
                                            call=call2)
        a5 = OfficerActivity.objects.create(officer_activity_id=5,
                                            activity_type=at2,
                                            time=dtparse('2014-01-16T10:10'),
                                            call_unit=cu1,
                                            call=None)
        a6 = OfficerActivity.objects.create(officer_activity_id=6,
                                            activity_type=at2,
                                            time=dtparse('2014-01-18T9:00'),
                                            call_unit=cu2,
                                            call=None)

        # In order for this to be realistic, for every busy activity,
        # we need to have an on duty activity
        a7 = OfficerActivity.objects.create(officer_activity_id=7,
                                            activity_type=at3,
                                            time=dtparse('2014-01-15T9:00'),
                                            call_unit=cu1,
                                            call=None)
        a8 = OfficerActivity.objects.create(officer_activity_id=8,
                                            activity_type=at3,
                                            time=dtparse('2014-01-15T9:10'),
                                            call_unit=cu2,
                                            call=None)
        a9 = OfficerActivity.objects.create(officer_activity_id=9,
                                            activity_type=at3,
                                            time=dtparse('2014-01-15T10:00'),
                                            call_unit=cu1,
                                            call=None)
        a10 = OfficerActivity.objects.create(officer_activity_id=10,
                                             activity_type=at3,
                                             time=dtparse('2014-01-16T9:50'),
                                             call_unit=cu2,
                                             call=None)
        a11 = OfficerActivity.objects.create(officer_activity_id=11,
                                             activity_type=at3,
                                             time=dtparse('2014-01-16T10:10'),
                                             call_unit=cu1,
                                             call=None)
        a12 = OfficerActivity.objects.create(officer_activity_id=12,
                                             activity_type=at3,
                                             time=dtparse('2014-01-18T9:00'),
                                             call_unit=cu2,
                                             call=None)

    def test_matches_expected_structure(self):
        """
        Make sure the results' structure matches our expectations.

        The results should be a dict with string representations of
        times as keys; each value should be another dict with
        activity names as keys.  Each of these nested dicts should
        have another dict as their value; these dicts should
        have metric names as keys and metric values (integers)
        as values.
        """
        overview = OfficerActivityOverview(q(''))
        results = overview.to_dict()['allocation_over_time']

        self.assertEqual(type(results), dict)

        # Keys should be strings, not datetimes,
        # so we can transmit them to the client
        self.assertEqual(type(list(results.keys())[0]), str)

        outer_value = list(results.values())[0]
        self.assertEqual(type(outer_value), dict)

        self.assertEqual(type(list(outer_value.keys())[0]), str)

        inner_value = list(outer_value.values())[0]
        self.assertEqual(type(inner_value), dict)

        self.assertEqual(type(list(inner_value.keys())[0]), str)
        self.assertEqual(type(list(inner_value.values())[0]), int)

    def test_distinguishes_activities(self):
        "Make sure we've covered all the types of activities."
        overview = OfficerActivityOverview(q(''))
        results = overview.to_dict()['allocation_over_time']

        self.assertEqual(
            sorted(set([k for time in results for k in results[time].keys()])),
            ['IN CALL - CITIZEN INITIATED', 'IN CALL - DIRECTED PATROL',
             'IN CALL - SELF INITIATED', 'ON DUTY', 'OUT OF SERVICE', 'PATROL'
             ])

    def test_evaluates_no_activity(self):
        # Should return 0 activities
        overview = OfficerActivityOverview(q('time__gte=2015-01-01'))
        results = overview.to_dict()['allocation_over_time']

        self.assertEqual(results, [])

    def test_evaluates_one_activity(self):
        # Should return 1 activity (a6)
        overview = OfficerActivityOverview(q('time__gte=2014-01-17'))
        results = overview.to_dict()['allocation_over_time']

        correct_results = {
            str(dtparse('9:00').time()):
                {
                    'IN CALL - CITIZEN INITIATED': {
                        'avg_volume': 0,
                        'total': 0,
                        'freq': 1
                    },
                    'IN CALL - SELF INITIATED': {
                        'avg_volume': 0,
                        'total': 0,
                        'freq': 1
                    },
                    'IN CALL - DIRECTED PATROL': {
                        'avg_volume': 0,
                        'total': 0,
                        'freq': 1
                    },
                    'OUT OF SERVICE': {
                        'avg_volume': 1.0,
                        'total': 1,
                        'freq': 1
                    },
                    'ON DUTY': {
                        'avg_volume': 1.0,
                        'total': 1,
                        'freq': 1
                    },
                    'PATROL': {
                        'avg_volume': 0.0,
                        'total': 0,
                        'freq': 1
                    }
                }
        }

        self.assertEqual(sorted(results.keys()),
                         sorted(correct_results.keys()))

        self.assertEqual(sorted(results.items()),
                         sorted(correct_results.items()))


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

    # These tests aren't relevant with the replacement of volume_over_time by
    # volume_by_date, but we may need them if we decide to scale volume_by_date
    # automatically again
    def test_call_volume_for_day(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2015-01-01&time_received__lte=2015-01-01"))
        assert overview.bounds == {"min_time": dtparse("2015-01-01T09:00"),
                                   "max_time": dtparse('2015-01-01T12:30')}

        assert_list_equiv(overview.volume_by_date(),
                          [{"date": dtparse("2015-01-01T09:00"), "volume": 1},
                           {"date": dtparse("2015-01-01T12:00"), "volume": 1}])

    def test_call_volume_for_multiple_days(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2015-01-01&time_received__lte=2015-01-09"))
        results = overview.volume_by_date()
        assert overview.bounds == {"min_time": dtparse("2015-01-01T09:00"),
                                   "max_time": dtparse('2015-01-08T09:00')}

        assert_list_equiv(results,
                          [{"date": dtparse("2015-01-01T00:00"), "volume": 2},
                           {"date": dtparse("2015-01-08T00:00"), "volume": 1}])

    def test_call_volume_for_month(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2015-01-01&time_received__lte=2015-02-02"))
        results = overview.volume_by_date()
        assert overview.bounds == {"min_time": dtparse("2015-01-01T09:00"),
                                   "max_time": dtparse('2015-02-01T09:00')}
        assert_list_equiv(results,
                          [{"date": dtparse("2015-01-01T00:00"), "volume": 2},
                           {"date": dtparse("2015-01-08T00:00"), "volume": 1},
                           {"date": dtparse("2015-02-01T00:00"), "volume": 1}])

    def test_call_volume_for_multiple_months(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2014-11-01&time_received__lte=2015-02-02"))
        results = overview.volume_by_date()
        assert overview.bounds == {"min_time": dtparse("2014-11-01T12:00"),
                                   "max_time": dtparse('2015-02-01T09:00')}

        assert_list_equiv(results,
                          [{"date": dtparse("2014-11-01"), "volume": 1},
                           {"date": dtparse("2015-01-01"), "volume": 2},
                           {"date": dtparse("2015-01-08"), "volume": 1},
                           {"date": dtparse("2015-02-01"), "volume": 1}])

    def test_call_volume_for_year(self):
        overview = CallVolumeOverview(
            q("time_received__gte=2014-01-01&time_received__lte=2015-02-02"))
        results = overview.volume_by_date()
        assert overview.bounds == {"min_time": dtparse("2014-01-15T09:00"),
                                   "max_time": dtparse('2015-02-01T09:00')}

        assert_list_equiv(results,
                          [{"date": dtparse("2014-01-01T00:00"), "volume": 1},
                           {"date": dtparse("2014-11-01T00:00"), "volume": 1},
                           {"date": dtparse("2015-01-01T00:00"), "volume": 3},
                           {"date": dtparse("2015-02-01T00:00"), "volume": 1}])
