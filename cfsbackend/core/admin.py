from django.db import models
from django.forms import TextInput
from django.contrib import admin
from .models import District, Beat, Nature, NatureGroup

# Register your models here.

class BeatInline(admin.StackedInline):
    model = Beat
    exclude = ('sector',)
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }

class BeatAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }

class DistrictAdmin(admin.ModelAdmin):
    inlines = [BeatInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }

class NatureAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }

class NatureInline(admin.StackedInline):
    model = Nature
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }

class NatureGroupAdmin(admin.ModelAdmin):
    inlines = [NatureInline]
    formfield_overrides = {
        models.TextField: {'widget': TextInput}
    }


admin.site.register(District, DistrictAdmin)
admin.site.register(Beat, BeatAdmin)
admin.site.register(Nature, NatureAdmin)
admin.site.register(NatureGroup, NatureGroupAdmin)