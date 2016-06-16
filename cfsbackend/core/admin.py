from django.db import models
from django.forms import TextInput
from django.contrib import admin
from .models import  Beat, District, Nature, NatureGroup, Bureau, CallSource, \
    CallUnit, ZipCode, City, Priority, CloseCode, Division, Officer, \
    OfficerActivity, OfficerActivityType, OOSCode, OutOfServicePeriod, Shift, Squad, \
    Transaction, \
    Unit


# Register your models here.

class BeatInline(admin.StackedInline):
    model = Beat
    exclude = ('sector',)
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(Beat)
class BeatAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    inlines = [BeatInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(Nature)
class NatureAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }

class NatureInline(admin.StackedInline):
    model = Nature
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(NatureGroup)
class NatureGroupAdmin(admin.ModelAdmin):
    inlines = [NatureInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


