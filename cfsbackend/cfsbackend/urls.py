"""
    cfsbackend URL Configuration
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from api import views
from dashboard.views import DashboardView

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'incidents', views.IncidentViewSet)

router.register(r'calls_sources', views.CallSourceViewSet)
router.register(r'calls_units', views.CallUnitViewSet)
router.register(r'nature', views.NatureViewSet)
router.register(r'close_codes', views.CloseCodeViewSet)
router.register(r'cities', views.CityViewSet)
router.register(r'oos_codes', views.OOSCodeViewSet)
router.register(r'out_of_service_periods', views.OutOfServicePeriodsViewSet)
router.register(r'sectors', views.SectorViewSet)
router.register(r'districts', views.DistrictViewSet)
router.register(r'beats', views.BeatViewSet)

router.register(r'calls', views.CallViewSet)

# You must use the optional 3rd parameter here. or otherwise it changes the URL for calls.
# the same holds true for any double-usage of the same queryset model in the ViewSet. 
router.register(r'calls_overview', views.CallOverviewViewSet, 'callsoverview')

urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^api/summary/', views.SummaryView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^$', DashboardView.as_view()),
]
