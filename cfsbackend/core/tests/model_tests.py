from dateutil.parser import parse as dtparse
from django.http import QueryDict
from django.test import TestCase
from .test_helpers import assert_list_equiv
from ..models import Call, CallOverview, Beat
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


class CallOverviewTest(TestCase):
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
        overview = CallOverview(q(''))
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
        overview = CallOverview(
            q("time_received__gte=2015-01-01&time_received__lte=2015-01-02"))
        assert overview.bounds == {"min_time": dtparse("2015-01-01T09:00"),
                                   "max_time": dtparse('2015-01-01T12:30')}

        assert_list_equiv(overview.volume_by_date(),
                          [{"date": dtparse("2015-01-01T00:00"), "volume": 2,
                            "average": 2}])

    def test_call_volume_for_multiple_days(self):
        overview = CallOverview(
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
        overview = CallOverview(
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
        overview = CallOverview(
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
        overview = CallOverview(
            q("time_received__gte=2014-01-01&time_received__lte=2015-02-02"))
        results = overview.volume_by_date()
        assert overview.bounds == {"min_time": dtparse("2014-01-15T09:00"),
                                   "max_time": dtparse('2015-02-01T09:00')}
        print(overview.volume_by_date())

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
        overview = CallOverview(
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
