# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.

from __future__ import unicode_literals

from django.db import models
from django.db.models import Q


class ModelWithDescr(models.Model):
    descr = models.TextField("Description", blank=False, null=False)

    def __str__(self):
        if self.descr:
            return self.descr
        else:
            return super().__str__()

    class Meta:
        abstract = True
        ordering = ['descr']


class Sector(ModelWithDescr):
    sector_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'sector'


class District(ModelWithDescr):
    district_id = models.IntegerField(primary_key=True)
    sector = models.ForeignKey(Sector, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'district'


class Beat(ModelWithDescr):
    beat_id = models.IntegerField(primary_key=True)
    district = models.ForeignKey(District, blank=True, null=True)
    sector = models.ForeignKey(Sector, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'beat'


class CallSource(ModelWithDescr):
    call_source_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'call_source'


class City(ModelWithDescr):
    city_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'city'


class Squad(ModelWithDescr):
    squad_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'squad'


class CallUnit(ModelWithDescr):
    call_unit_id = models.IntegerField(primary_key=True)
    squad = models.ForeignKey(Squad, blank=True, null=True,
                              db_column="squad_id",
                              related_name="+")
    beat = models.ForeignKey(Beat, blank=True, null=True,
                             db_column="beat_id",
                             related_name="+")
    district = models.ForeignKey(District, blank=True, null=True,
                             db_column="district_id",
                             related_name="+")

    class Meta:
        managed = False
        db_table = 'call_unit'


class Nature(ModelWithDescr):
    nature_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'nature'


class CloseCode(ModelWithDescr):
    close_code_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'close_code'


class OOSCode(ModelWithDescr):
    oos_code_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'oos_code'


class OutOfServicePeriod(models.Model):
    oos_id = models.IntegerField(primary_key=True)
    call_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                  db_column="call_unit_id",
                                  related_name="+")
    shift_unit_id = models.BigIntegerField(blank=True, null=True)
    oos_code = models.ForeignKey(OOSCode, blank=True, null=True,
                                 db_column="oos_code_id",
                                 related_name="+")
    location = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'out_of_service'


class Shift(models.Model):
    shift_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'shift'


class Officer(models.Model):
    officer_id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    name_aka = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'officer'


class Bureau(ModelWithDescr):
    bureau_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'bureau'


class Division(ModelWithDescr):
    division_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'division'


class Unit(ModelWithDescr):
    unit_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'unit'


class ShiftUnit(models.Model):
    shift_unit_id = models.IntegerField(primary_key=True)
    call_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                  db_column="call_unit_id",
                                  related_name="+")
    officer = models.ForeignKey(Officer, blank=True, null=True,
                                db_column="officer_id",
                                related_name="+")
    in_time = models.DateTimeField(blank=True, null=True)
    out_time = models.DateTimeField(blank=True, null=True)
    bureau = models.ForeignKey(Bureau, blank=True, null=True,
                               db_column="bureau_id",
                               related_name="+")
    division = models.ForeignKey(Division, blank=True, null=True,
                                 db_column="division_id",
                                 related_name="+")
    unit = models.ForeignKey(Unit, blank=True, null=True,
                             db_column="unit_id",
                             related_name="+")
    shift = models.ForeignKey(Shift, blank=True, null=True,
                              db_column="shift_id",
                              related_name="+")

    class Meta:
        managed = False
        db_table = 'shift_unit'


# Primary Classes

class CallQuerySet(models.QuerySet):
    def squad(self, value):
        if value:
            query = Q(primary_unit_id=value) | Q(
                first_dispatched_id=value) | Q(
                reporting_unit_id=value)
            return self.filter(query)
        else:
            return self

    def initiated_by(self, value):
        if str(value) == "0":
            return self.filter(
                call_source=CallSource.objects.get(descr="Self Initiated"))
        elif str(value) == "1":
            return self.exclude(
                call_source=CallSource.objects.get(descr="Self Initiated"))
        else:
            return self

    def shift(self, value):
        if str(value) == "0":
            query = Q(hour_received__gte=6) & Q(hour_received__lt=18)
            return self.filter(query)
        elif str(value) == "1":
            query = Q(hour_received__lt=6) | Q(hour_received__gte=18)
            return self.filter(query)
        else:
            return self


class Call(models.Model):
    objects = CallQuerySet.as_manager()

    call_id = models.BigIntegerField(primary_key=True)
    year_received = models.IntegerField(blank=True, null=True)
    month_received = models.IntegerField(blank=True, null=True)
    week_received = models.IntegerField(blank=True, null=True)
    dow_received = models.IntegerField(blank=True, null=True)
    hour_received = models.IntegerField(blank=True, null=True)
    case_id = models.BigIntegerField(blank=True, null=True)
    call_source = models.ForeignKey('CallSource', blank=True, null=True)
    primary_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                     related_name="+")
    first_dispatched = models.ForeignKey(CallUnit, blank=True, null=True,
                                         related_name="+")
    reporting_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                       related_name="+")
    street_num = models.IntegerField(blank=True, null=True)
    street_name = models.TextField(blank=True, null=True)
    city = models.ForeignKey('City', blank=True, null=True)
    zip_code = models.ForeignKey('ZipCode', blank=True, null=True)
    crossroad1 = models.TextField(blank=True, null=True)
    crossroad2 = models.TextField(blank=True, null=True)
    geox = models.FloatField(blank=True, null=True)
    geoy = models.FloatField(blank=True, null=True)
    beat = models.ForeignKey(Beat, blank=True, null=True, related_name='+')
    district = models.ForeignKey('District', blank=True, null=True,
                                 related_name='+')
    sector = models.ForeignKey('Sector', blank=True, null=True,
                               related_name='+')
    business = models.TextField(blank=True, null=True)
    nature = models.ForeignKey('Nature', blank=True, null=True)
    priority = models.ForeignKey('Priority', blank=True, null=True)
    report_only = models.NullBooleanField()
    cancelled = models.NullBooleanField()
    time_received = models.DateTimeField(blank=True, null=True)
    time_routed = models.DateTimeField(blank=True, null=True)
    time_finished = models.DateTimeField(blank=True, null=True)
    first_unit_dispatch = models.DateTimeField(blank=True, null=True)
    first_unit_enroute = models.DateTimeField(blank=True, null=True)
    first_unit_arrive = models.DateTimeField(blank=True, null=True)
    first_unit_transport = models.DateTimeField(blank=True, null=True)
    last_unit_clear = models.DateTimeField(blank=True, null=True)
    time_closed = models.DateTimeField(blank=True, null=True)
    close_code = models.ForeignKey('CloseCode', blank=True, null=True)
    close_comments = models.TextField(blank=True, null=True)
    incident = models.ForeignKey('Incident', blank=True, null=True)
    officer_response_time = models.DurationField(blank=True, null=True)
    overall_response_time = models.DurationField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'call'


class InCallPeriod(models.Model):
    in_call_id = models.IntegerField(primary_key=True)
    call_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                  db_column="call_unit_id",
                                  related_name="+")
    shift = models.ForeignKey(Shift, blank=True, null=True,
                              db_column="shift_id",
                              related_name="+")
    call = models.ForeignKey(Call, blank=True, null=True,
                             db_column="call_id",
                             related_name="+")
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'in_call'


class OfficerActivityType(ModelWithDescr):
    officer_activity_type_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'officer_activity_type'


class OfficerActivity(models.Model):
    officer_activity_id = models.IntegerField(primary_key=True,
                                db_column="discrete_officer_activity_id")
    call_unit = models.ForeignKey(CallUnit, blank=True, null=True,
                                  db_column="call_unit_id",
                                  related_name="+")
    time = models.DateTimeField(blank=True, null=True,
                                db_column="time_")
    activity_type = models.ForeignKey(OfficerActivityType,
                                      db_column="officer_activity_type_id",
                                      related_name="+")
    call = models.ForeignKey(Call, blank=True, null=True,
                             db_column="call_id",
                             related_name="+")

    class Meta:
        managed = False
        db_table = 'discrete_officer_activity'


class Incident(models.Model):
    incident_id = models.BigIntegerField(primary_key=True)
    case_id = models.BigIntegerField(unique=True, blank=True, null=True)
    time_filed = models.DateTimeField(blank=True, null=True)
    month_filed = models.IntegerField(blank=True, null=True)
    week_filed = models.IntegerField(blank=True, null=True)
    dow_filed = models.IntegerField(blank=True, null=True)
    street_num = models.IntegerField(blank=True, null=True)
    street_name = models.TextField(blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True)
    # zip_code = models.ForeignKey('ZipCode', blank=True, null=True)
    # zipcode     = models.IntegerField(blank=True, null=True, db_column="zip")
    geox = models.FloatField(blank=True, null=True)
    geoy = models.FloatField(blank=True, null=True)
    beat = models.ForeignKey(Beat, blank=True, null=True)
    district = models.ForeignKey(District, blank=True, null=True)
    sector = models.ForeignKey(Sector, blank=True, null=True)
    # premise    = models.ForeignKey('Premise', blank=True, null=True)
    # weapon     = models.ForeignKey('Weapon', blank=True, null=True)
    domestic = models.NullBooleanField()
    juvenile = models.NullBooleanField()
    gang_related = models.NullBooleanField()
    # emp_bureau = models.ForeignKey(Bureau, blank=True, null=True)
    # emp_division = models.ForeignKey(Division, blank=True, null=True)
    # emp_unit = models.ForeignKey('Unit', blank=True, null=True)
    num_officers = models.IntegerField(blank=True, null=True)
    # investigation_status = models.ForeignKey('InvestigationStatus', blank=True, null=True)
    # investigator_unit = models.ForeignKey('Unit', blank=True, null=True)
    # case_status = models.ForeignKey(CaseStatus, blank=True, null=True)
    # ucr_code = models.IntegerField(blank=True, null=True)
    # ucr_descr = models.ForeignKey('UcrDescr', blank=True, null=True)
    committed = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'incident'


class Priority(ModelWithDescr):
    priority_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'priority'


class ZipCode(ModelWithDescr):
    zip_code_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'zip_code'
