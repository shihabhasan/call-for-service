"""
    cfsbackend URL Configuration
"""
from django.conf.urls import include, url
from rest_framework import routers

from core import views

router = routers.DefaultRouter()
router.register(r'calls', views.CallViewSet)

urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^api/call_volume/$', views.CallVolumeView.as_view()),
    url(r'^api/response_time/$', views.CallResponseTimeView.as_view()),
    url(r'^api/call_map/$', views.CallMapView.as_view()),
    url(r'^api/officer_allocation/', views.OfficerAllocationView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^call_volume$', views.CallVolumeView.as_view()),
    url(r'^response_time$', views.ResponseTimeView.as_view()),
    url(r'^$', views.DashboardView.as_view()),
    url(r'^officer_allocation$', views.OfficerAllocationDashboardView.as_view()),
]
