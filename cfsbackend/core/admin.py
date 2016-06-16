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


@admin.register(Bureau)
class BureauAdmin(admin.ModelAdmin):
    pass


@admin.register(CallSource)
class CallSourceAdmin(admin.ModelAdmin):
    pass


@admin.register(CallUnit)
class CallUnitAdmin(admin.ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(CloseCode)
class CloseCodeAdmin(admin.ModelAdmin):
    pass


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    pass


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    pass


@admin.register(OfficerActivity)
class OfficerActivityAdmin(admin.ModelAdmin):
    pass


@admin.register(OfficerActivityType)
class OfficerActivityTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(OOSCode)
class OOSCodeAdmin(admin.ModelAdmin):
    pass


@admin.register(OutOfServicePeriod)
class OutOfServicePeriodAdmin(admin.ModelAdmin):
    pass


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    pass


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    pass


@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(ZipCode)
class ZipCodeAdmin(admin.ModelAdmin):
    pass