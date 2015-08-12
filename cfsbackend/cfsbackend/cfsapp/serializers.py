from django.contrib.auth.models import User, Group
from .models import Incident, Call, City
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class CitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ('city_id', 'descr')

class IncidentSerializer(serializers.HyperlinkedModelSerializer):
    
    city = CitySerializer()
    
    class Meta:
        model = Incident
        fields = ('incident_id', 'case_id', 'time_filed', 'month_filed', 'week_filed', 'dow_filed', 'street_num', 'street_name', 'zip', 'city',
        	'geox', 'geoy', 'beat', 'district', 'sector', 'domestic', 'juvenile', 'gang_related', 'num_officers', 'ucr_code', 'committed')

class CallSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Call
        fields = ('call_id', 'month_received', 'week_received', 'dow_received', 'hour_received', 'case_id', 'street_num', 'street_name', 'zip', 'crossroad1', 'crossroad2', 'geox', 'geoy', 'beat', 'district', 'sector', 'business', 'priority', 'report_only', 'cancelled', 'time_received', 'time_routed', 'time_finished', 'first_unit_dispatch', 'first_unit_enroute', 'first_unit_arrive', 'first_unit_transport', 'last_unit_clear', 'time_closed', 'close_comments')

# Testing reduced payload
class CallOverviewSerializer(serializers.HyperlinkedModelSerializer):
    m = serializers.IntegerField(source='month_received')
    w = serializers.IntegerField(source='week_received')
    d = serializers.IntegerField(source='dow_received')
    h = serializers.IntegerField(source='hour_received')
    n = serializers.IntegerField(source='call_id__count')

    class Meta:
        model = Call
        fields = ('m','w','d','h','n')

