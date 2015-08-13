from django.contrib.auth.models import User, Group

from .models import * # Incident, Call, City, CallSource, CallUnit, CloseCode, Nature
from rest_framework import serializers

from collections import OrderedDict
from rest_framework.fields import SkipField

# Documentation here: http://www.django-rest-framework.org/api-guide/serializers/

class NonNullSerializer(serializers.ModelSerializer):

    """
    This overrides the HyperlinkedModelSerializer to skips keys with null values.
    http://stackoverflow.com/a/28870066/373402
    """

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            if attribute is not None:
                represenation = field.to_representation(attribute)
                if represenation is None:
                    # Do not seralize empty objects
                    continue
                if isinstance(represenation, list) and not represenation:
                   # Do not serialize empty lists
                   continue
                ret[field.field_name] = represenation

        return ret


class SectorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sector
        fields = ('url', 'sector_id', 'descr')

class DistrictSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = District
        fields = ('url', 'district_id', 'sector', 'descr')

class BeatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Beat
        fields = ('url', 'beat_id', 'district', 'sector', 'descr')

# Support Serializers

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
        fields = ('url','city_id', 'descr')

class CallSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CallSource
        fields = ('url', 'call_source_id', 'descr')

class CallUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CallUnit
        fields = ('url', 'call_unit_id', 'descr')

class NatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Nature 
        fields = ('url', 'nature_id', 'descr')

class CloseCodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CloseCode 
        fields = ('url', 'close_code_id', 'descr')

class OOSCodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OOSCode
        fields = ('url', 'oos_code_id', 'descr')

class OutOfServicePeriodsSerializer(NonNullSerializer):

    call_unit = CallUnitSerializer(read_only=True,allow_null=False)
    oos_code  = OOSCodeSerializer(read_only=True, allow_null=False)

    class Meta:
        model = OutOfServicePeriods
        read_only_fields = ('url', 'oos_id', 'call_unit', 'shift_unit_id', 'oos_code', 'location', 'comments', 'start_time', 'end_time', 'duration')

# Main Class / Analytic Serializers

class IncidentSerializer(serializers.HyperlinkedModelSerializer):
    
    city = CitySerializer(read_only=True)
    
    class Meta:
        model = Incident
        read_only_fields = ('incident_id', 'case_id', 'time_filed', 'month_filed', 'week_filed', 'dow_filed', 'street_num', 'street_name', 'zipcode', 'city',
        	'geox', 'geoy', 'beat', 'district', 'sector', 'domestic', 'juvenile', 'gang_related', 'num_officers', 'ucr_code', 'committed')

class CallSerializer(NonNullSerializer):

    city             = CitySerializer(read_only=True)
    call_source      = CallSourceSerializer(read_only=True)
    primary_unit     = CallUnitSerializer(read_only=True,allow_null=False)
    first_dispatched = CallUnitSerializer(read_only=True)
    reporting_unit   = CallUnitSerializer(read_only=True,allow_null=True)
    close_code       = CloseCodeSerializer(read_only=True,allow_null=True)
    nature           = NatureSerializer(read_only=True,allow_null=True)

    beat             = BeatSerializer(read_only=True, allow_null=True)
    district         = DistrictSerializer(read_only=True, allow_null=True)
    sector           = SectorSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Call
        read_only_fields = ('call_id', 'city', 'call_source', 'primary_unit', 'first_dispatched', 'close_code', 'nature', 'reporting_unit', 'month_received', 'week_received', 'dow_received', 'hour_received', 'case_id', 'street_num', 'street_name', 'zipcode', 'crossroad1', 'crossroad2', 'geox', 'geoy', 'beat', 'district', 'sector', 'business', 'priority', 'report_only', 'cancelled', 'time_received', 'time_routed', 'time_finished', 'first_unit_dispatch', 'first_unit_enroute', 'first_unit_arrive', 'first_unit_transport', 'last_unit_clear', 'time_closed', 'close_comments')

class CallOverviewSerializer(serializers.HyperlinkedModelSerializer):
    m = serializers.IntegerField(source='month_received')
    w = serializers.IntegerField(source='week_received')
    d = serializers.IntegerField(source='dow_received')
    h = serializers.IntegerField(source='hour_received')
    n = serializers.IntegerField(source='call_id__count')

    class Meta:
        model = Call
        fields = ('m','w','d','h','n')



