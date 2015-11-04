from django.db.models import Count
from url_filter.integrations.drf import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Call, Sector, District, Beat, City, \
    CallSource, CallUnit, Nature, CloseCode, \
    CallOverview, OfficerActivityOverview
from ..filters import CallFilterSet
from .. import serializers


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


class CallOverviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for reduced data payload for summary page. Note that it aggregates by count of calls
    """
    queryset = Call.objects.values('month_received', 'week_received', 'dow_received', 'hour_received').annotate(
        Count('call_id'))
    serializer_class = serializers.CallOverviewSerializer


class SectorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that shows details about all Sectors. Not used in analysis.
    """
    queryset = Sector.objects.all()
    serializer_class = serializers.SectorSerializer


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that shows details about policing districts.
    """
    queryset = District.objects.all()
    serializer_class = serializers.DistrictSerializer


class BeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that shows details about policing beats.
    """
    queryset = Beat.objects.all()
    serializer_class = serializers.BeatSerializer


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows calls to be viewed or edited.
    """
    queryset = City.objects.all()
    serializer_class = serializers.CitySerializer


class CallSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for showing the possible call sources for a 911 call.
    """
    queryset = CallSource.objects.all()
    serializer_class = serializers.CallSourceSerializer


class CallUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for showing the units that respond to a call.
    """
    queryset = CallUnit.objects.all()
    serializer_class = serializers.CallUnitSerializer


class NatureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for showing the nature of a call.
    """
    queryset = Nature.objects.all()
    serializer_class = serializers.NatureSerializer


class CloseCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for showing the code applied to a call that when it was closed.
    """
    queryset = CloseCode.objects.all()
    serializer_class = serializers.CloseCodeSerializer


class OverviewView(APIView):
    """
    Gives all the information needed for the overview dashboard based off
    of user-submitted filters.
    """

    def get(self, request, format=None):
        overview = CallOverview(request.GET)
        return Response(overview.to_dict())

class OfficerAllocationView(APIView):
    """
    Gives all the information needed for the officer allocation dashboard based off
    of user-submitted filters.
    """

    def get(self, request, format=None):
        overview = OfficerActivityOverview(request.GET)
        return Response(overview.to_dict())
