from django.forms import ModelChoiceField
from django_filters import FilterSet, DateFromToRangeFilter, MethodFilter, \
    RangeFilter, ModelChoiceFilter
from django_filters.fields import RangeField
from django.db.models import Q
from django import forms

from .models import Call, CallUnit, ZipCode


class DurationRangeField(RangeField):
    def __init__(self, *args, **kwargs):
        fields = (
            forms.DurationField(),
            forms.DurationField())
        super().__init__(fields, *args, **kwargs)


class ChoiceMethodFilter(MethodFilter):
    field_class = forms.ChoiceField


class DurationRangeFilter(RangeFilter):
    field_class = DurationRangeField

    def filter(self, qs, value):
        if value:
            if value.start is not None and value.stop is not None:
                lookup = '%s__range' % self.name
                return self.get_method(qs)(
                    **{lookup: (value.start, value.stop)})
            else:

                if value.start is not None:
                    qs = self.get_method(qs)(
                        **{'%s__gte' % self.name: value.start})
                if value.stop is not None:
                    qs = self.get_method(qs)(
                        **{'%s__lte' % self.name: value.stop})
        return qs


class CallFilter(FilterSet):
    time_received = DateFromToRangeFilter()
    time_routed = DateFromToRangeFilter()
    time_finished = DateFromToRangeFilter()
    time_closed = DateFromToRangeFilter()
    response_time = DurationRangeFilter()
    unit = ChoiceMethodFilter(action='filter_unit',
                              choices=['', '---------'] + list(
                                  CallUnit.objects.all().values_list(
                                      'call_unit_id', 'descr')))

    class Meta:
        model = Call
        fields = ['zip_code', 'district', 'sector', 'beat',
                  'call_source', 'nature', 'priority', 'close_code',
                  'primary_unit', 'first_dispatched', 'reporting_unit',
                  'cancelled'
                  ]

    def filter_unit(self, queryset, value):
        if value:
            query = Q(primary_unit_id=value) | Q(first_dispatched_id=value) | Q(
                reporting_unit_id=value)
            return queryset.filter(query)
        else:
            return queryset


class SummaryFilter(FilterSet):
    class Meta:
        model = Call
        fields = ['month_received', 'dow_received', 'hour_received']
