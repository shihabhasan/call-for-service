from django.forms import ModelChoiceField
from django import forms
from url_filter.filtersets import ModelFilterSet
from url_filter.fields import MultipleValuesField
from url_filter.filters import Filter
from django.db.models import Q

from .models import Call, CallUnit, Squad, ZipCode, CallSource, Nature, \
    District, Beat, Sector, Priority, CloseCode, OfficerActivity


def get_form_field_for_type(ftype):
    type_map = {
        "text": forms.CharField(),
        "date": forms.DateField(),
        "duration": forms.DurationField(),
        "boolean": forms.BooleanField(),
    }
    return type_map.get(ftype, forms.CharField())


def create_rel_filterset(model_name):
    model = globals()[model_name]
    name = model.__name__ + "FilterSet"
    Meta = type('Meta', (object,),
                {"model": model, "fields": [model._meta.pk.name]})
    rel_filterset = type(name, (ModelFilterSet,), {"Meta": Meta})
    return rel_filterset


def create_filterset(model, definition, name=None):
    if name is None:
        name = model.__name__ + "FilterSet"
    Meta = type('Meta', (object,),
                {"model": model, "fields": []})

    attrs = {}
    for f in definition:
        if f.get("rel"):
            try:
                filter = globals()[f["rel"] + "FilterSet"]()
            except KeyError:
                filter_class = create_rel_filterset(f["rel"])
                filter = filter_class()
        else:
            ftype = f.get("type", "text")
            form_field = get_form_field_for_type(ftype)
            source = f.get("source", f["name"])
            lookups = f.get("lookups", ["exact"])
            default_lookup = f.get("default_lookup", "exact")
            filter = Filter(source=source, form_field=form_field,
                            lookups=lookups, default_lookup=default_lookup)

        attrs[f["name"]] = filter


    attrs["Meta"] = Meta
    attrs["definition"] = definition

    return type(name, (ModelFilterSet,), attrs)


class SquadFilterSet(ModelFilterSet):
    class Meta:
        model = Squad
        fields = ["squad_id"]


class CallUnitFilterSet(ModelFilterSet):
    class Meta:
        model = CallUnit
        fields = ["call_unit_id", "squad"]

CallFilterSet = create_filterset(
    Call,
    [
        {"name": "time_received", "type": "date", "lookups": ["gte", "lte"],
         "default_lookup": "gte"},
        {"name": "time_routed", "type": "date", "lookups": ["gte", "lte"],
         "default_lookup": "gte"},
        {"name": "time_finished", "type": "date", "lookups": ["gte", "lte"],
         "default_lookup": "gte"},
        {"name": "time_closed", "type": "date", "lookups": ["gte", "lte"],
         "default_lookup": "gte"},
        {"name": "officer_response_time", "type": "duration",
         "lookups": ["gte", "lte"], "default_lookup": "gte"},
        {"name": "overall_response_time", "type": "duration",
         "lookups": ["gte", "lte"], "default_lookup": "gte"},
        {"name": "district", "rel": "District"},
        {"name": "beat", "rel": "Beat"},
        {"name": "zip_code", "rel": "ZipCode", "label": "ZIP code"},
        {"name": "call_source", "rel": "CallSource"},
        {"name": "nature", "rel": "Nature"},
        {"name": "priority", "rel": "Priority"},
        {"name": "close_code", "rel": "CloseCode"},
        {"name": "primary_unit", "rel": "CallUnit"},
        {"name": "first_dispatched", "rel": "CallUnit"},
        {"name": "reporting_unit", "rel": "CallUnit"},
        {"name": "cancelled", "type": "boolean"}
    ]
)

OfficerActivityFilterSet = create_filterset(
    OfficerActivity,
    [
        {"name": "call_unit", "rel": "CallUnit"},
        {"name": "time", "type": "date", "lookups": ["gte", "lte"],
         "default_lookup": "gte"},
        {"name": "activity", "type": "text", "lookups": ["exact"],
         "default_lookup": "exact"},
        {"name": "call", "rel": "Call"}
    ]
)


#     unit = ChoiceMethodFilter(action='filter_unit',
#                               choices=CallUnit.objects.all().values_list('call_unit_id', 'descr'))
#     squad = ChoiceMethodFilter(action='filter_squad',
#                               choices=Squad.objects.all().values_list('squad_id', 'descr'))
#
#     initiated_by = ChoiceMethodFilter(label="Initiated by",
#                                       action="filter_initiated_by",
#                                       choices=[('Self', 'Self'), ('Citizen', 'Citizen')])
#
#     def filter_unit(self, queryset, value):
#         if value:
#             query = Q(primary_unit_id=value) | Q(first_dispatched_id=value) | Q(
#                 reporting_unit_id=value)
#             return queryset.filter(query)
#         else:
#             return queryset
#
#     def filter_squad(self, queryset, value):
#         if value:
#             query = Q(primary_unit__squad_id=value) | Q(first_dispatched__squad_id=value) | Q(
#                 reporting_unit__squad_id=value)
#             return queryset.filter(query)
#         else:
#             return queryset
#
#     def filter_initiated_by(self, queryset, value):
#         if value == "Self":
#             return queryset.filter(call_source=CallSource.objects.get(descr="Self Initiated"))
#         elif value == "Citizen":
#             return queryset.exclude(call_source=CallSource.objects.get(descr="Self Initiated"))
#         else:
#             return queryset
#



# class DurationRangeField(RangeField):
#     def __init__(self, *args, **kwargs):
#         fields = (
#             forms.DurationField(),
#             forms.DurationField())
#         super().__init__(fields, *args, **kwargs)
#
#
# class ChoiceMethodFilter(MethodFilter):
#     field_class = forms.ChoiceField
#
#
# class DurationRangeFilter(RangeFilter):
#     field_class = DurationRangeField
#
#     def filter(self, qs, value):
#         if value:
#             if value.start is not None and value.stop is not None:
#                 lookup = '%s__range' % self.name
#                 return self.get_method(qs)(
#                     **{lookup: (value.start, value.stop)})
#             else:
#
#                 if value.start is not None:
#                     qs = self.get_method(qs)(
#                         **{'%s__gte' % self.name: value.start})
#                 if value.stop is not None:
#                     qs = self.get_method(qs)(
#                         **{'%s__lte' % self.name: value.stop})
#         return qs


# class SummaryFilter(FilterSet):
#     class Meta:
#         model = Call
#         fields = ['month_received', 'dow_received', 'hour_received']
