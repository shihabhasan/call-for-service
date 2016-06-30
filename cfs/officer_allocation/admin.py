from django.db import models
from django.forms import TextInput
from django.contrib import admin
from .models import InCallPeriod, OfficerActivity, OfficerActivityType, \
    OOSCode, OutOfServicePeriod

class OutOfServicePeriodInline(admin.TabularInline):
    model = OutOfServicePeriod
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }

@admin.register(InCallPeriod)
class InCallPeriodAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(OfficerActivity)
class OfficerActivityAdmin(admin.ModelAdmin):
    pass


@admin.register(OfficerActivityType)
class OfficerActivityTypeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(OOSCode)
class OOSCodeAdmin(admin.ModelAdmin):
    list_display = ('descr', 'code',)
    inlines = [OutOfServicePeriodInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


@admin.register(OutOfServicePeriod)
class OutOfServicePeriodAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }
