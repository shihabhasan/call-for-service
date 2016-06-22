from django.db import models
from django.forms import TextInput
from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import  Beat, Bureau, CallSource, CallUnit, City, CloseCode, \
    District, Division, Nature, NatureGroup,  \
    Officer, \
    Priority, Shift, ShiftUnit, SiteConfiguration, Squad, \
    Transaction, Unit, ZipCode

admin.site.register(SiteConfiguration, SingletonModelAdmin)


### model inline classes

class BeatInline(admin.TabularInline):
    model = Beat
    extra = 0
    exclude = ('sector',)
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


class CallUnitInline(admin.TabularInline):
    model = CallUnit
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


class NatureInline(admin.StackedInline):
    model = Nature
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }

class ShiftUnitInline(admin.TabularInline):
    model = ShiftUnit
    extra = 0


### model admin classes

@admin.register(Beat)
class BeatAdmin(admin.ModelAdmin):
    list_display = ('descr', 'district',)
    inlines = [CallUnitInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(Bureau)
class BureauAdmin(admin.ModelAdmin):
    list_display = ('descr', 'code',)
    inlines = [ShiftUnitInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(CallSource)
class CallSourceAdmin(admin.ModelAdmin):
    list_display = ('descr', 'code',)
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(CallUnit)
class CallUnitAdmin(admin.ModelAdmin):
    list_display = ('descr', 'squad', 'beat', 'district',)
    inlines = [ShiftUnitInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(CloseCode)
class CloseCodeAdmin(admin.ModelAdmin):
    list_display = ('descr', 'code',)
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    exclude = ('sector',)
    inlines = [BeatInline, CallUnitInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput(attrs={'size':'50'})}
    }


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('descr', 'code',)
    inlines = [ShiftUnitInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(Nature)
class NatureAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(NatureGroup)
class NatureGroupAdmin(admin.ModelAdmin):
    inlines = [NatureInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_aka',)
    inlines = [ShiftUnitInline]


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    inlines = [ShiftUnitInline]


@admin.register(ShiftUnit)
class ShiftUnitAdmin(admin.ModelAdmin):
    pass


@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('code',)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('descr', 'code',)
    inlines = [ShiftUnitInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(ZipCode)
class ZipCodeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }