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

class Weapon(models.Model):
    weapon_id = models.AutoField(primary_key=True)
    descr = models.TextField(blank=True, null=True)
    weapon_group = models.ForeignKey('WeaponGroup', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'weapon'


class WeaponGroup(models.Model):
    weapon_group_id = models.AutoField(primary_key=True)
    descr = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'weapon_group'

class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    descr = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'city'

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
    zip = models.IntegerField(blank=True, null=True)
    geox = models.FloatField(blank=True, null=True)
    geoy = models.FloatField(blank=True, null=True)
    beat = models.TextField(blank=True, null=True)
    district = models.TextField(blank=True, null=True)
    sector = models.TextField(blank=True, null=True)
    #premise = models.ForeignKey('Premise', blank=True, null=True)
    weapon = models.ForeignKey('Weapon', blank=True, null=True)
    domestic = models.NullBooleanField()
    juvenile = models.NullBooleanField()
    gang_related = models.NullBooleanField()
    #emp_bureau = models.ForeignKey(Bureau, blank=True, null=True)
    #emp_division = models.ForeignKey(Division, blank=True, null=True)
    #emp_unit = models.ForeignKey('Unit', blank=True, null=True)
    num_officers = models.IntegerField(blank=True, null=True)
    #investigation_status = models.ForeignKey('InvestigationStatus', blank=True, null=True)
    #investigator_unit = models.ForeignKey('Unit', blank=True, null=True)
    #case_status = models.ForeignKey(CaseStatus, blank=True, null=True)
    ucr_code = models.IntegerField(blank=True, null=True)
    #ucr_descr = models.ForeignKey('UcrDescr', blank=True, null=True)
    committed = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'incident'

