import json
from django.shortcuts import render_to_response
from django.views.generic import View, TemplateView
from core import models
from ..filters import CallFilterSet, OfficerActivityFilterSet


def filter_json(filter_set):
    fields = filter_set.definition
    out = {"fields": [f for f in fields if not f['name'] == 'call']}
    refs = {}

    for field in fields:
        if field.get('rel') and not refs.get(field['rel']):

            # Enabling filtering on related fields will be tricky for
            # the Call model, since it's not just a descr we need to
            # display.  We'll bypass that for now.
            if field['rel'] == 'Call':
                continue

            model = getattr(models, field['rel'])
            pk_name = model._meta.pk.name
            refs[field['rel']] = list(
                model.objects.all().order_by("descr").values_list(pk_name,
                                                                  "descr"))

    out["refs"] = refs
    return json.dumps(out)


class CallVolumeView(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("overview.html",
                                  dict(form=filter_json(CallFilterSet)))


class ResponseTimeView(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("response_time.html",
                                  dict(form=filter_json(CallFilterSet)))


class PredictiveView(TemplateView):
    template_name = "predictive.html"

    def get_context_data(self, **kwargs):
        context = super(PredictiveView, self).get_context_data(**kwargs)
        context['form'] = filter_json()
        return context


class MapView(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("map.html",
                                  dict(form=filter_json(CallFilterSet)))

class OfficerAllocationDashboardView(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("officer_allocation.html",
                                  dict(form=filter_json(OfficerActivityFilterSet)))
