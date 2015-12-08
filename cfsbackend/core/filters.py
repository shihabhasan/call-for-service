import datetime
from django.db.models.constants import LOOKUP_SEP
from django import forms
from url_filter.filtersets import ModelFilterSet
from url_filter.filters import Filter
from url_filter.backends.django import DjangoFilterBackend
from . import models


class BetterDjangoFilterBackend(DjangoFilterBackend):
    def prepare_spec(self, spec):
        if spec.lookup == "exact":
            return LOOKUP_SEP.join(spec.components)
        else:
            return '{}{}{}'.format(
                LOOKUP_SEP.join(spec.components),
                LOOKUP_SEP,
                spec.lookup,
            )

    def prepare_value(self, spec):
        if spec.lookup == "lte" and isinstance(spec.value, datetime.date):
            value = spec.value
            value = datetime.datetime(year=value.year, month=value.month,
                                      day=value.day, hour=0, minute=0, second=0)
            value = value + datetime.timedelta(days=1, microseconds=-1)
        else:
            value = spec.value

        return value

    def filter(self):
        include = {self.prepare_spec(i): self.prepare_value(i) for i in
                   self.includes}
        exclude = {self.prepare_spec(i): self.prepare_value(i) for i in
                   self.excludes}

        qs = self.queryset

        for k, v in include.items():
            try:
                qs = getattr(qs, k)(v)
            except AttributeError:
                qs = qs.filter(**{k: v})
        for k, v in exclude.items():
            try:
                qs = getattr(qs, k)(v, exclude=True)
            except AttributeError:
                qs = qs.exclude(**{k: v})

        return qs

    def bind(self, specs):
        self.specs = specs


def get_form_field_for_type(ftype):
    type_map = {
        "text": forms.CharField(),
        "date": forms.DateField(),
        "daterange": forms.DateField(),
        "duration": forms.DurationField(),
        "boolean": forms.BooleanField(required=False),
        "select": forms.ChoiceField(),
    }
    return type_map.get(ftype, forms.CharField())


def create_rel_filterset(model_name):
    model = getattr(models, model_name)
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
        if f.get("type") == "daterange":
            f['lookups'] = ["gte", "lte"]

        if f.get("rel") and not f.get("method"):
            try:
                filter = globals()[f["rel"] + "FilterSet"]()
            except KeyError:
                filter_class = create_rel_filterset(f["rel"])
                filter = filter_class()
        else:
            ftype = f.get("type", "text")
            form_field = get_form_field_for_type(ftype)
            if f.get("options"):
                form_field._set_choices(f.get("options"))
            source = f.get("source", f["name"])
            lookups = f.get("lookups", ["exact"])
            default_lookup = f.get("default_lookup", lookups[0])
            filter = Filter(source=source, form_field=form_field,
                            lookups=lookups, default_lookup=default_lookup)

        attrs[f["name"]] = filter

    attrs["Meta"] = Meta
    attrs["definition"] = definition
    attrs["filter_backend_class"] = BetterDjangoFilterBackend

    return type(name, (ModelFilterSet,), attrs)

class SquadFilterSet(ModelFilterSet):
    class Meta:
        model = models.Squad
        fields = ["squad_id"]


class CallUnitFilterSet(ModelFilterSet):
    class Meta:
        model = models.CallUnit
        fields = ["call_unit_id", "squad", "beat", "district"]


CallFilterSet = create_filterset(
    models.Call,
    [
        {"name": "time_received", "type": "daterange"},
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
        {"name": "cancelled", "type": "boolean"},
        {"name": "dow_received", "label": "Day of Week", "type": "select",
         "options": [
             [0, "Monday"], [1, "Tuesday"], [2, "Wednesday"], [3, "Thursday"],
             [4, "Friday"], [5, "Saturday"], [6, "Sunday"]
         ]},
        {"name": "squad", "rel": "Squad", "method": True, "type": "choice",
         "lookups": ["exact"]},
        {"name": "initiated_by", "type": "select", "method": True,
         "lookups": ["exact"],
         "options": [[0, "Officer"], [1, "Citizen"]]},
        {"name": "shift", "type": "select", "method": True, "lookups": ["exact"],
         "options": [[0, "Shift 1"], [1, "Shift 2"]]},
    ]
)

OfficerActivityFilterSet = create_filterset(
    models.OfficerActivity,
    [
        {"name": "call_unit", "rel": "CallUnit"},
        {"name": "call_unit__beat", "label": "Beat", "rel": "Beat"},
        {"name": "call_unit__district", "label": "District", "rel": "District"},
        {"name": "time", "type": "daterange"},
    ]
)
