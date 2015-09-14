from django_filters import FilterSet, DateFromToRangeFilter
from .models import Call, Incident


class CallFilter(FilterSet):
    time_received = DateFromToRangeFilter()
    time_closed = DateFromToRangeFilter()

    class Meta:
        model = Call
        fields = ['time_received', 'time_routed', 'time_finished', 'time_closed', 'city', 'district', 'beat', 'sector',
                  'call_source', 'nature', 'priority', 'close_code', 'zip_code']


class SummaryFilter(FilterSet):
    class Meta:
        model = Call
        fields = ['month_received', 'dow_received', 'hour_received']
