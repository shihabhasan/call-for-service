from dateutil.parser import parse as dtparse
from django.test import TestCase
from ..models import Call, CallOverview


def assert_list_equiv(this, that):
    """
    Lists are having difficulty with equivalence, so let's try this.
    """
    assert len(this) == len(that)
    for i in range(len(this)):
        assert this[i] == that[i]


class CallOverviewTest(TestCase):
    def setUp(self):
        Call.objects.create(call_id=1, time_received='2014-01-15T09:00', dow_received=2, hour_received=9)  # W
        Call.objects.create(call_id=2, time_received='2015-01-01T09:00', dow_received=3, hour_received=9)  # Th
        Call.objects.create(call_id=3, time_received='2015-01-01T12:30', dow_received=3, hour_received=12)  # Th
        Call.objects.create(call_id=4, time_received='2015-01-08T09:00', dow_received=3, hour_received=9)  # Th
        Call.objects.create(call_id=5, time_received='2015-02-01T09:00', dow_received=6, hour_received=9)  # Su

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
        assert results['period_size'] == 'week'
        assert results['bounds'] == {"min_time": dtparse("2015-01-01T09:00"),
                                     "max_time": dtparse('2015-02-01T09:00')}

        assert_list_equiv(results['results'],
                          [{"period_start": dtparse("2014-12-29T00:00"), "period_volume": 2},
                           {"period_start": dtparse("2015-01-05T00:00"), "period_volume": 1},
                           {"period_start": dtparse("2015-01-26T00:00"), "period_volume": 1}])

    def test_call_volume_for_year(self):
        overview = CallOverview({"time_received_0": "2014-01-01", "time_received_1": "2015-02-01"})
        results = overview.to_dict()['volume_over_time']
        assert results['period_size'] == 'month'
        assert results['bounds'] == {"min_time": dtparse("2014-01-15T09:00"),
                                     "max_time": dtparse('2015-02-01T09:00')}

        assert_list_equiv(results['results'],
                          [{"period_start": dtparse("2014-01-01T00:00"), "period_volume": 1},
                           {"period_start": dtparse("2015-01-01T00:00"), "period_volume": 3},
                           {"period_start": dtparse("2015-02-01T00:00"), "period_volume": 1}])

    def test_day_hour_heatmap(self):
        overview = CallOverview({"time_received_0": "2014-01-01", "time_received_1": "2015-02-01"})
        results = overview.to_dict()['day_hour_heatmap']

        print(repr(results))

        assert_list_equiv(results, [
            {'dow_received': 2, 'hour_received': 9, 'volume': 1},
            {'dow_received': 3, 'hour_received': 9, 'volume': 2},
            {'dow_received': 3, 'hour_received': 12, 'volume': 1},
            {'dow_received': 6, 'hour_received': 9, 'volume': 1},
        ])
