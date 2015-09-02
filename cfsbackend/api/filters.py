from django_filters import FilterSet, DateFromToRangeFilter
from .models import Call, Incident

class IncidentFilter(FilterSet):
	time_filed = DateFromToRangeFilter()

	class Meta:
		model = Incident
		fields = ['time_filed']

class CallFilter(FilterSet):
    time_received = DateFromToRangeFilter()
    time_routed = DateFromToRangeFilter()
    time_finished = DateFromToRangeFilter()
    time_closed = DateFromToRangeFilter()

    class Meta:
        model = Call
        fields = ['time_received', 'time_routed', 'time_finished', 'time_closed']


class SummaryFilter(FilterSet):
    class Meta:
        model = Call
        fields = ['month_received', 'dow_received', 'hour_received']