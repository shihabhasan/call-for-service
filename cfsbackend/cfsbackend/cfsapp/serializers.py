from django.contrib.auth.models import User, Group
from .models import Incident
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class IncidentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Incident
        fields = ('incident_id', 'case_id', 'time_filed', 'month_filed', 'week_filed', 'dow_filed', 'street_num', 'street_name', 'geox', 'geoy', 'beat', 'district', 'sector', 'domestic', 'juvenile', 'gang_related', 'num_officers', 'ucr_code', 'committed')