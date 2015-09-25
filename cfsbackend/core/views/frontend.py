from django.shortcuts import render_to_response
from django.views.generic import View

from ..filters import CallFilter
from ..forms import JSONForm


class DashboardView(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("index.html",
                                  dict(form=JSONForm(CallFilter().form)))
