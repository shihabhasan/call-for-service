from django.shortcuts import render_to_response
from django.views.generic import View, TemplateView

from ..filters import CallFilter
from ..forms import JSONForm


class CallListView(TemplateView):
  def get(self, request, *args, **kwargs):
        return render_to_response("calls.html",
                                  dict(form=JSONForm(CallFilter().form)))

class DashboardView(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("index.html",
                                  dict(form=JSONForm(CallFilter().form)))

