from dateutil.parser import parse as dtparse
from django.test import TestCase
from ..models import Call, CallOverview, Beat
from datetime import timedelta


def assert_list_equiv(this, that):
    """
    Lists are having difficulty with equivalence, so let's try this.
    """
    assert len(this) == len(that)
    for i in range(len(this)):
        assert this[i] == that[i]


def create_call(**kwargs):
    try:
        time_received = dtparse(kwargs['time_received'])
    except KeyError:
        raise ValueError("You must include a time_received value.")

    kwargs['dow_received'] = time_received.weekday()
    kwargs['hour_received'] = time_received.hour

    return Call.objects.create(**kwargs)


class CallOverviewTest(TestCase):
    def setUp(self):
        b1 = Beat.objects.create(beat_id=1, descr="B1")
        b2 = Beat.objects.create(beat_id=2, descr="B2")
        create_call(call_id=1, time_received='2014-01-15T09:00',
                    response_time=timedelta(0, 120),
                    beat=b1)
        create_call(call_id=2, time_received='2015-01-01T09:00',
                    response_time=timedelta(0, 600),
                    beat=b1)
        create_call(call_id=3, time_received='2015-01-01T12:30',
                    response_time=timedelta(0, 900),
                    beat=b2)
        create_call(call_id=4, time_received='2015-01-08T09:00',
                    beat=b1)
        create_call(call_id=5, time_received='2015-02-01T09:00',
                    beat=b2)
        create_call(call_id=6, time_received='2014-11-01T12:00',
                    beat=b1)

    def test_call_volume_for_day(self):
        overview = CallOverview({"time_received_0": "2015-01-01", "time_received_1": "2015-01-01"})
        results = overview.to_dict()['volume_over_time']
        assert results['period_size'] == 'hour'
        assert results['bounds'] == {"min_time": dtparse("2015-01-01T09:00"),
                                     "max_time": dtparse('2015-01-01T12:30')}

        assert_list_equiv(results['results'],
                          [{"period_start": dtparse("2015-01-01T09:00"), "period_volume": 1},
                           {"period_start": dtparse("2015-01-01T12:00"), "period_volume": 1}])

    def test_call_volume_for_multiple_days(self):
        overview = CallOverview({"time_received_0": "2015-01-01", "time_received_1": "2015-01-08"})
        results = overview.to_dict()['volume_over_time']
        assert results['period_size'] == 'day'
        assert results['bounds'] == {"min_time": dtparse("2015-01-01T09:00"),
                                     "max_time": dtparse('2015-01-08T09:00')}

        assert_list_equiv(results['results'],
                          [{"period_start": dtparse("2015-01-01T00:00"), "period_volume": 2},
                           {"period_start": dtparse("2015-01-08T00:00"), "period_volume": 1}])

    def test_call_volume_for_month(self):
        overview = CallOverview({"time_received_0": "2015-01-01", "time_received_1": "2015-02-01"})
        results = overview.to_dict()['volume_over_time']
        assert results['period_size'] == 'day'
        assert results['bounds'] == {"min_time": dtparse("2015-01-01T09:00"),
                                     "max_time": dtparse('2015-02-01T09:00')}

        assert_list_equiv(results['results'],
                          [{"period_start": dtparse("2015-01-01T00:00"), "period_volume": 2},
                           {"period_start": dtparse("2015-01-08T00:00"), "period_volume": 1},
                           {"period_start": dtparse("2015-02-01T00:00"), "period_volume": 1}])

    def test_call_volume_for_multiple_months(self):
        overview = CallOverview({"time_received_0": "2014-11-01", "time_received_1": "2015-02-01"})
        results = overview.to_dict()['volume_over_time']
        assert results['period_size'] == 'week'
        assert results['bounds'] == {"min_time": dtparse("2014-11-01T12:00"),
                                     "max_time": dtparse('2015-02-01T09:00')}

        assert_list_equiv(results['results'],
                          [{"period_start": dtparse("2014-10-27"), "period_volume": 1},
                           {"period_start": dtparse("2014-12-29"), "period_volume": 2},
                           {"period_start": dtparse("2015-01-05"), "period_volume": 1},
                           {"period_start": dtparse("2015-01-26"), "period_volume": 1}])

    def test_call_volume_for_year(self):
        overview = CallOverview({"time_received_0": "2014-01-01", "time_received_1": "2015-02-01"})
        results = overview.to_dict()['volume_over_time']
        assert results['period_size'] == 'month'
        assert results['bounds'] == {"min_time": dtparse("2014-01-15T09:00"),
                                     "max_time": dtparse('2015-02-01T09:00')}

        assert_list_equiv(results['results'],
                          [{"period_start": dtparse("2014-01-01T00:00"), "period_volume": 1},
                           {"period_start": dtparse("2014-11-01T00:00"), "period_volume": 1},
                           {"period_start": dtparse("2015-01-01T00:00"), "period_volume": 3},
                           {"period_start": dtparse("2015-02-01T00:00"), "period_volume": 1}])

    def test_day_hour_heatmap(self):
        overview = CallOverview({"time_received_0": "2015-01-01", "time_received_1": "2015-02-01"})
        results = overview.to_dict()['day_hour_heatmap']

        assert_list_equiv(results, [
            {'dow_received': 3, 'hour_received': 9, 'volume': 0.4, 'freq': 5, 'total': 2},
            {'dow_received': 3, 'hour_received': 12, 'volume': 0.2, 'freq': 5, 'total': 1},
            {'dow_received': 6, 'hour_received': 9, 'volume': 0.2, 'freq': 5, 'total': 1},
        ])

    def test_response_time_by_beat(self):
        overview = CallOverview({"time_received_0": "2014-01-01", "time_received_1": "2015-02-01"})
        results = overview.to_dict()['response_time_by_beat']

        assert_list_equiv(results, [
            {'beat': 1, 'beat__descr': 'B1', 'mean': 360, 'missing': 2},
            {'beat': 2, 'beat__descr': 'B2', 'mean': 900, 'missing': 1}
        ])
