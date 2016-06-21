from django.shortcuts import render, render_to_response

# Create your views here.
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.views import APIView

from core import models
from core.views import build_filter
from officer_allocation.filters import OfficerActivityFilterSet
from officer_allocation.summaries import OfficerActivityOverview


class APIOfficerAllocationView(APIView):
    """Powers officer allocation dashboard."""

    def get(self, request, format=None):
        overview = OfficerActivityOverview(request.GET)
        return Response(overview.to_dict())


class OfficerAllocationDashboardView(View):
    def get(self, request, *args, **kwargs):
        filter_obj = build_filter(OfficerActivityFilterSet)

        # We want only the values of CallUnit where squad isn't null.
        # We don't want to show a bunch of bogus units for filtering.
        filter_obj['refs']['CallUnit'] = list(
            models.CallUnit.objects
                .filter(squad__isnull=False)
                .order_by('descr')
                .values_list('call_unit_id', 'descr'))

        return render_to_response("dashboard.html",
                                  dict(asset_chunk="officer_allocation",
                                       form=filter_obj))
