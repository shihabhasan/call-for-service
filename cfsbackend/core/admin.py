from django.contrib import admin

# Register your models here.
from solo.admin import SingletonModelAdmin
from .models import SiteConfiguration

admin.site.register(SiteConfiguration, SingletonModelAdmin)