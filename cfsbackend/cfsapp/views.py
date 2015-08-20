from django.shortcuts import render

from django.contrib.auth.models import User, Group
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *  # Incident, City, Call, CallSource, CallUnit, Nature, CloseCode
import \
    cfsbackend.cfsapp.serializers as ser  # import UserSerializer, GroupSerializer, IncidentSerializer, CallSerializer, CallOverviewSerializer, CallSourceSerializer, CallUnitSerializer
import django_filters


# The order in which these appear determines the order in which they appear in the self-documenting API

class SectorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that shows details about all Sectors. Not used in analysis.
    """
    queryset = Sector.objects.all()
    serializer_class = ser.SectorSerializer


class DistrictViewSet(viewsets.ModelViewSet):
    """
    API endpoint that shows details about policing districts. 
    """
    queryset = District.objects.all()
    serializer_class = ser.DistrictSerializer


class BeatViewSet(viewsets.ModelViewSet):
    """
    API endpoint that shows details about policing beats.
    """
    queryset = Beat.objects.all()
    serializer_class = ser.BeatSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = ser.UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = ser.GroupSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows incidents to be viewed or edited.
    """
    queryset = Incident.objects.all()
    serializer_class = ser.IncidentSerializer


class CityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows calls to be viewed or edited.
    """
    queryset = City.objects.all()
    serializer_class = ser.CitySerializer


class CallViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows calls to be viewed or edited.
    """
    queryset = Call.objects.all()
    serializer_class = ser.CallSerializer


class CallOverviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reduced data payload for summary page. Note that it aggregates by count of calls
    """
    queryset = Call.objects.values('month_received', 'week_received', 'dow_received', 'hour_received').annotate(
        Count('call_id'))
    serializer_class = ser.CallOverviewSerializer


class CallSourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for showing the possible call sources for a 911 call.
    """
    queryset = CallSource.objects.all()
    serializer_class = ser.CallSourceSerializer


class CallUnitViewSet(viewsets.ModelViewSet):
    """
    API endpoint for showing the units that respond to a call.
    """
    queryset = CallUnit.objects.all()
    serializer_class = ser.CallUnitSerializer


class NatureViewSet(viewsets.ModelViewSet):
    """
    API endpoint for showing the nature of a call.
    """
    queryset = Nature.objects.all()
    serializer_class = ser.NatureSerializer


class CloseCodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for showing the code applied to a call that when it was closed.
    """
    queryset = CloseCode.objects.all()
    serializer_class = ser.CloseCodeSerializer


class OOSCodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for showing the out of service codes and their descriptions.
    """
    queryset = OOSCode.objects.all()
    serializer_class = ser.OOSCodeSerializer


class OutOfServicePeriodsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for showing the out of service periods.
    """
    queryset = OutOfServicePeriods.objects.all()
    serializer_class = ser.OutOfServicePeriodsSerializer


class CallFilter(django_filters.FilterSet):
    class Meta:
        model = Call
        fields = ['month_received', 'dow_received', 'hour_received']


class SummaryView(APIView):
    """
    Gives summary statistics about calls for service based off of user-
    submitted filters.
    """

    def get(self, request, format=None):
        filter = CallFilter(request.GET, queryset=Call.objects.all())
        summary = CallSummary(filter.qs)
        return Response(summary.to_dict())
