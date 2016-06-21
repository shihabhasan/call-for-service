from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from url_filter.integrations.drf import DjangoFilterBackend

from .. import serializers
from ..filters import CallFilterSet
from ..models import Call
from ..summaries import CallResponseTimeOverview, \
    CallVolumeOverview, CallMapOverview


class CallPagination(PageNumberPagination):
    page_size = 50


class CallViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows calls to be viewed.
    """
    queryset = Call.objects.order_by('time_received') \
        .select_related('district') \
        .select_related('beat') \
        .select_related('city') \
        .select_related('zip_code') \
        .select_related('priority') \
        .select_related('call_source') \
        .select_related('nature') \
        .select_related('nature__nature_group') \
        .select_related('close_code') \
        .select_related('primary_unit') \
        .select_related('first_dispatched') \
        .select_related('reporting_unit')

    serializer_class = serializers.CallSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = CallFilterSet
    pagination_class = CallPagination


class APICallResponseTimeView(APIView):
    """Powers response time dashboard."""

    def get(self, request, format=None):
        overview = CallResponseTimeOverview(request.GET)
        return Response(overview.to_dict())


class APICallVolumeView(APIView):
    """Powers call volume dashboard."""

    def get(self, request, format=None):
        overview = CallVolumeOverview(request.GET)
        return Response(overview.to_dict())


class APICallMapView(APIView):
    def get(self, request, format=None):
        overview = CallMapOverview(request.GET)
        return Response(overview.to_dict())
