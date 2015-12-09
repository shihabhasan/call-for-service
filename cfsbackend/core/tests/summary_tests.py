from datetime import timedelta
from django.test import TestCase
from django.db.models import Model
from dateutil.parser import parse as dtparse
from core.summaries import OfficerActivityOverview, CallVolumeOverview
from .test_helpers import assert_list_equiv, create_call, q, create_officer_activity
from ..models import Beat, CallUnit, OfficerActivity, Nature, \
    OfficerActivityType, CallSource, District


class OfficerActivityOverviewTest(TestCase):
    def setUp(self):
        cs1 = CallSource.objects.create(call_source_id=1,
                descr='Citizen Initiated', code='C')
        cs2 = CallSource.objects.create(call_source_id=2,
                descr='Self Initiated', code='S')
        self.n1 = Nature.objects.create(nature_id=1, descr='Robbery')
        self.n2 = Nature.objects.create(nature_id=2, descr='Homicide')
        self.call1 = create_call(call_id=1,
                                 time_received='2014-01-15T9:00',
                                 nature=self.n1,
                                 call_source=cs1)
        self.call2 = create_call(call_id=2,
                                 time_received='2014-03-18T3:00',
                                 nature=self.n2,
                                 call_source=cs1)

        self.b1 = Beat.objects.create(beat_id=1, descr='B1')
        self.b2 = Beat.objects.create(beat_id=2, descr='B2')

        self.d1 = District.objects.create(district_id=1, descr='D1')
        self.d2 = District.objects.create(district_id=2, descr='D2')

        self.cu1 = CallUnit.objects.create(call_unit_id=1, descr='A1',
                                           beat=self.b1, district=self.d1)
        self.cu2 = CallUnit.objects.create(call_unit_id=2, descr='B2',
                                           beat=self.b2, district=self.d2)

        self.at1 = OfficerActivityType.objects.create(
            officer_activity_type_id=1,
            descr="IN CALL - CITIZEN INITIATED")
        self.at2 = OfficerActivityType.objects.create(
            officer_activity_type_id=2,
            descr="OUT OF SERVICE")
        self.at3 = OfficerActivityType.objects.create(
            officer_activity_type_id=3,
            descr="ON DUTY")


        self.a1 = create_officer_activity(activity_type=self.at1,
                                                 time=dtparse(
                                                     '2014-01-15T9:00'),
                                                 call_unit=self.cu1,
                                                 call=self.call1)
        self.a2 = create_officer_activity(activity_type=self.at1,
                                                 time=dtparse(
                                                     '2014-01-15T9:10'),
                                                 call_unit=self.cu2,
                                                 call=self.call1)
        self.a3 = create_officer_activity(activity_type=self.at1,
                                                 time=dtparse(
                                                     '2014-01-15T10:00'),
                                                 call_unit=self.cu1,
                                                 call=self.call2)
        self.a4 = create_officer_activity(activity_type=self.at1,
                                                 time=dtparse(
                                                     '2014-01-16T9:50'),
                                                 call_unit=self.cu2,
                                                 call=self.call2)
        self.a5 = create_officer_activity(activity_type=self.at2,
                                                 time=dtparse(
                                                     '2014-01-16T10:10'),
                                                 call_unit=self.cu1,
                                                 call=None)
        self.a6 = create_officer_activity(activity_type=self.at2,
                                                 time=dtparse(
                                                     '2014-01-18T9:00'),
                                                 call_unit=self.cu2,
                                                 call=None)

        # In order for this to be realistic, for every busy activity,
        # we need to have an on duty activity
        self.a7 = create_officer_activity(activity_type=self.at3,
                                            time=dtparse('2014-01-15T9:00'),
                                            call_unit=self.cu1,
                                            call=None)
        self.a8 = create_officer_activity(activity_type=self.at3,
                                            time=dtparse('2014-01-15T9:10'),
                                            call_unit=self.cu2,
                                            call=None)
        self.a9 = create_officer_activity(activity_type=self.at3,
                                            time=dtparse('2014-01-15T10:00'),
                                            call_unit=self.cu1,
                                            call=None)
        self.a10 = create_officer_activity(activity_type=self.at3,
                                             time=dtparse('2014-01-16T9:50'),
                                             call_unit=self.cu2,
                                             call=None)
        self.a11 = create_officer_activity(activity_type=self.at3,
                                             time=dtparse('2014-01-16T10:10'),
                                             call_unit=self.cu1,
                                             call=None)
        self.a12 = create_officer_activity(activity_type=self.at3,
                                             time=dtparse('2014-01-18T9:00'),
                                             call_unit=self.cu2,
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
