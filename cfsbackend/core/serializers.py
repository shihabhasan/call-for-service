from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField, CharField

from .models import Call, CallUnit, Nature, CloseCode, CallSource, Beat, \
    District, Priority, NatureGroup, Squad


class NonNullSerializer(serializers.ModelSerializer):
    """
    This overrides the ModelSerializer to skip keys with null values.

    http://stackoverflow.com/a/28870066/373402
    """

    def to_representation(self, instance):
        """Object instance -> Dict of primitive datatypes."""
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if
                  not field.write_only]

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


class SquadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Squad
        fields = ('squad_id', 'descr')


class CallUnitSerializer(serializers.ModelSerializer):
    squad = SquadSerializer(read_only=True, allow_null=True)

    class Meta:
        model = CallUnit
        fields = ('call_unit_id', 'squad', 'descr')


class NatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nature
        fields = ('nature_id', 'descr')


class CloseCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloseCode
        fields = ('close_code_id', 'descr')


class CallSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallSource
        fields = ('call_source_id', 'descr')


class BeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beat
        fields = ('beat_id', 'descr')


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('district_id', 'descr')


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ('priority_id', 'descr')


class NatureGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NatureGroup
        fields = ('nature_group_id', 'descr')


class CallExportSerializer(NonNullSerializer):
    city = CharField(source="city.descr", read_only=True)
    zip_code = CharField(source="zip_code.descr", read_only=True)

    primary_unit = CharField(source="primary_unit.descr", read_only=True)
    first_dispatched = CharField(source="first_dispatched.descr", read_only=True)
    reporting_unit = CharField(source="reporting_unit.descr", read_only=True)
    nature = CharField(source="nature.descr", read_only=True)

    beat = CharField(source="beat.descr", read_only=True)
    district = CharField(source="district.descr", read_only=True)
    priority = CharField(source="priority.descr", read_only=True)
    call_source = CharField(source="call_source.descr", read_only=True)
    nature_group = CharField(source="nature.nature_group.descr", read_only=True)
    close_code = CharField(source="close_code.descr", read_only=True)

    class Meta:
        model = Call
        fields = (
            'call_id', 'city', 'zip_code', 'district', 'beat',
            'street_num', 'street_name', 'crossroad1', 'crossroad2', 'geox',
            'geoy',
            'call_source', 'primary_unit', 'first_dispatched', 'close_code',
            'nature', 'nature_group',
            'reporting_unit', 'month_received', 'week_received', 'dow_received',
            'hour_received', 'case_id',
            'business', 'priority', 'report_only', 'cancelled', 'time_received',
            'time_routed',
            'time_finished', 'first_unit_dispatch', 'first_unit_enroute',
            'first_unit_arrive', 'first_unit_transport',
            'last_unit_clear', 'time_closed', 'officer_response_time',
            'overall_response_time')


class CallSerializer(NonNullSerializer):
    city = CharField(source="city.descr", read_only=True)
    zip_code = CharField(source="zip_code.descr", read_only=True)

    primary_unit = CallUnitSerializer(read_only=True, allow_null=False)
    first_dispatched = CallUnitSerializer(read_only=True)
    reporting_unit = CallUnitSerializer(read_only=True, allow_null=True)
    nature = NatureSerializer(read_only=True, allow_null=True)

    beat = BeatSerializer(allow_null=True, read_only=True)
    district = DistrictSerializer(allow_null=True, read_only=True)
    priority = PrioritySerializer(allow_null=True, read_only=True)
    call_source = CallSourceSerializer(allow_null=True, read_only=True)
    nature_group = NatureGroupSerializer(source='nature.nature_group', allow_null=True, read_only=True)

    class Meta:
        model = Call
        fields = (
            'call_id', 'city', 'zip_code', 'district', 'beat',
            'street_num', 'street_name', 'crossroad1', 'crossroad2', 'geox',
            'geoy',
            'call_source', 'primary_unit', 'first_dispatched', 'close_code',
            'nature', 'nature_group',
            'reporting_unit', 'month_received', 'week_received', 'dow_received',
            'hour_received', 'case_id',
            'business', 'priority', 'report_only', 'cancelled', 'time_received',
            'time_routed',
            'time_finished', 'first_unit_dispatch', 'first_unit_enroute',
            'first_unit_arrive', 'first_unit_transport',
            'last_unit_clear', 'time_closed', 'officer_response_time',
            'overall_response_time')
