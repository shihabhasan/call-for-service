from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField, CharField
from rest_framework.serializers import Serializer

from .models import Call, Sector, District, Beat, City, \
    CallSource, CallUnit, Nature, CloseCode


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
    sector = CharField(source="sector.descr", read_only=True)

    class Meta:
        model = District
        fields = ('sector', 'descr')


class BeatSerializer(serializers.HyperlinkedModelSerializer):
    district = CharField(source="district.descr", read_only=True)
    sector = CharField(source="sector.descr", read_only=True)

    class Meta:
        model = Beat
        fields = ('district', 'sector', 'descr')


class CitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ('url', 'city_id', 'descr')


class CallSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CallSource
        fields = ('url', 'call_source_id', 'descr')


class CallUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CallUnit
        fields = ('call_unit_id', 'descr')


class NatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Nature
        fields = ('nature_id', 'descr')


class CloseCodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CloseCode
        fields = ('close_code_id', 'descr')


class CallSerializer(NonNullSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='call-detail',
        lookup_field='pk'
    )
    city = CharField(source="city.descr", read_only=True)
    call_source = CharField(source="call_source.descr", read_only=True)
    zip_code = CharField(source="zip_code.descr", read_only=True)
    beat = CharField(source="beat.descr", read_only=True)
    district = CharField(source="district.descr", read_only=True)
    sector = CharField(source="sector.descr", read_only=True)

    primary_unit = CallUnitSerializer(read_only=True, allow_null=False)
    first_dispatched = CallUnitSerializer(read_only=True)
    reporting_unit = CallUnitSerializer(read_only=True, allow_null=True)
    close_code = CloseCodeSerializer(read_only=True, allow_null=True)
    nature = NatureSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Call
        fields = (
            'url', 'call_id', 'city', 'zip_code', 'sector', 'district', 'beat',
            'street_num', 'street_name',  'crossroad1', 'crossroad2', 'geox', 'geoy',
            'call_source', 'primary_unit', 'first_dispatched', 'close_code', 'nature',
            'reporting_unit', 'month_received', 'week_received', 'dow_received', 'hour_received', 'case_id',
            'business', 'priority', 'report_only', 'cancelled', 'time_received', 'time_routed',
            'time_finished', 'first_unit_dispatch', 'first_unit_enroute', 'first_unit_arrive', 'first_unit_transport',
            'last_unit_clear', 'time_closed', 'response_time')


class CallOverviewSerializer(serializers.HyperlinkedModelSerializer):
    m = serializers.IntegerField(source='month_received')
    w = serializers.IntegerField(source='week_received')
    d = serializers.IntegerField(source='dow_received')
    h = serializers.IntegerField(source='hour_received')
    n = serializers.IntegerField(source='call_id__count')

    class Meta:
        model = Call
        fields = ('m', 'w', 'd', 'h', 'n')
