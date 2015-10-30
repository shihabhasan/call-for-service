import json

from django.shortcuts import render_to_response
from django.views.generic import View, TemplateView
from core import models

from ..filters import CallFilterSet


def filter_json():
    fields = CallFilterSet.definition
    out = {"fields": fields}
    refs = {}

    for field in fields:
        if field.get('rel') and not refs.get(field['rel']):
            model = getattr(models, field['rel'])
            pk_name = model._meta.pk.name
            refs[field['rel']] = list(
                model.objects.all().order_by("descr").values_list(pk_name, "descr"))

    out["refs"] = refs
    return json.dumps(out)


class CallListView(TemplateView):
    template_name = "calls.html"

    def get_context_data(self, **kwargs):
        context = super(CallListView, self).get_context_data(**kwargs)
        context['form'] = filter_json()
        return context


class DashboardView(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("overview.html",
                                  dict(form=filter_json()))


class ResponseTimeView(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("response_time.html",
                                  dict(form=filter_json()))


class PredictiveView(TemplateView):
    template_name = "predictive.html"

    def get_context_data(self, **kwargs):
        context = super(PredictiveView, self).get_context_data(**kwargs)
        context['form'] = filter_json()
        return context
