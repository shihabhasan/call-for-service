from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from url_filter.integrations.drf import DjangoFilterBackend

from .. import serializers
from ..filters import CallFilterSet
from ..models import Call
from ..summaries import CallResponseTimeOverview, \
    CallVolumeOverview, OfficerActivityOverview


class CallPagination(PageNumberPagination):
    page_size = 50


class CallViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows calls to be viewed.

    You can filter by date/time using `time_received__gte` for received start
    date and `time_received__lte` for received end date.
    """
    queryset = Call.objects.order_by('time_received')
    serializer_class = serializers.CallSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = CallFilterSet
    pagination_class = CallPagination


class APICallResponseTimeView(APIView):
    """Powers response time dashboard."""

    def get(self, request, format=None):
        overview = CallResponseTimeOverview(request.GET)
        return Response(overview.to_dict())


class APIOfficerAllocationView(APIView):
    """Powers officer allocation dashboard."""

    def get(self, request, format=None):
        overview = OfficerActivityOverview(request.GET)
        return Response(overview.to_dict())


class APICallVolumeView(APIView):
    """Powers call volume dashboard."""

    def get(self, request, format=None):
        overview = CallVolumeOverview(request.GET)
        return Response(overview.to_dict())
