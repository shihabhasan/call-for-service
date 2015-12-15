from django.db.models import F
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from url_filter.integrations.drf import DjangoFilterBackend

from .. import serializers
from ..filters import CallFilterSet
from ..models import Call
from ..summaries import CallResponseTimeOverview, \
    CallVolumeOverview, OfficerActivityOverview


class CallViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows calls to be viewed.

    You can filter by:

    * `district`
    * `beat`
    * `sector`
    * `zip code`
    * `call source`
    * `nature`
    * `priority`
    * `close code`

    You can filter by date/time using:

    * `time_received__gte` for received start date
      and `time_received__lte` for received end date.
    * `time_closed__gte` for closed start date
      and `time_closed__lte` for closed end date.
    """
    queryset = Call.objects.order_by('time_received')
    serializer_class = serializers.CallSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = CallFilterSet

from rest_framework_msgpack.renderers import MessagePackRenderer
from rest_framework.renderers import JSONRenderer


class APICallMapView(APIView):
    """
    Get the call data needed to display the call map.
    """

    renderer_classes = (JSONRenderer, MessagePackRenderer,)

    def build_response(self, qs):
        res = {"count": qs.count()}
        cols = ['call_id',
                'time_received',
                'call_source__descr',
                'street_num',
                'street_name',
                'geox',
                'geoy',
                'business',
                'nature__descr',
                'priority__descr',
                'close_code__descr',
                'officer_response_time']
        calls = qs.values_list(*cols)
        calls = [list(call) for call in calls]
        for call in calls:
            call[1] = call[1].strftime("%c")
            call[-1] = call[-1].total_seconds() if call[-1] else None
        res['columns'] = cols
        res['calls'] = calls
        return res

    def get(self, request, format=None):
        filter = CallFilterSet(data=request.GET, queryset=Call.objects.all())
        qs = filter.filter()

        if qs.count() > 10000:
            return Response({"count": qs.count(),
                             "error": "Too many calls to display"})
        else:
            return Response(self.build_response(qs))


class APICallResponseTimeView(APIView):
    """
    Gives all the information needed for the response time dashboard based off
    of user-submitted filters.
    """

    def get(self, request, format=None):
        overview = CallResponseTimeOverview(request.GET)
        return Response(overview.to_dict())


class APIOfficerAllocationView(APIView):
    """
    Gives all the information needed for the officer allocation dashboard based off
    of user-submitted filters.
    """

    def get(self, request, format=None):
        overview = OfficerActivityOverview(request.GET)
        return Response(overview.to_dict())


class APICallVolumeView(APIView):
    """
    Gives all the information needed for the call volume dashboard based off
    of user-submitted filters.
    """

    def get(self, request, format=None):
        overview = CallVolumeOverview(request.GET)
        return Response(overview.to_dict())
