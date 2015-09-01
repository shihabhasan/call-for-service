from django_filters import FilterSet, DateFromToRangeFilter
from .models import Call


class CallFilter(FilterSet):
    time_received = DateFromToRangeFilter()
    class Meta:
        model = Call
        fields = ['time_received']


class SummaryFilter(FilterSet):
    class Meta:
        model = Call
        fields = ['month_received', 'dow_received', 'hour_received']