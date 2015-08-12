from django.shortcuts import render

from django.contrib.auth.models import User, Group
from django.db.models import Count
from rest_framework import viewsets
from .models import Incident, Call, CallSource, CallUnit
from cfsbackend.cfsapp.serializers import UserSerializer, GroupSerializer, IncidentSerializer, CallSerializer, CallOverviewSerializer, CallSourceSerializer, CallUnitSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class IncidentViewSet(viewsets.ModelViewSet):
	"""
    API endpoint that allows incidents to be viewed or edited.
    """
	queryset = Incident.objects.all()
	serializer_class = IncidentSerializer

class CallViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows calls to be viewed or edited.
    """
    queryset = Call.objects.all()
    serializer_class = CallSerializer

class CallOverviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reduced data payload for summary page. Note that it aggregates by count of calls
    """
    queryset = Call.objects.values('month_received','week_received','dow_received','hour_received').annotate(Count('call_id'))
    serializer_class = CallOverviewSerializer

class CallSourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for showing the possible call sources for a 911 call.
    """
    queryset = CallSource.objects.all()
    serializer_class = CallSourceSerializer

class CallUnitViewSet(viewsets.ModelViewSet):
    """
    API endpoint for showing the units that respond to a call.
    """
    queryset = CallUnit.objects.all()
    serializer_class = CallUnitSerializer