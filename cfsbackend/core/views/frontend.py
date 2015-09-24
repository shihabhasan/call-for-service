from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = "index.html"

class CallListView(TemplateView):
    template_name = "calls.html"
