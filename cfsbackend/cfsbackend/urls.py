"""cfsbackend URL Configuration."""

from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from core import views

router = routers.DefaultRouter()
router.register(r'calls', views.CallViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/call_volume/$', views.APICallVolumeView.as_view()),
    url(r'^api/response_time/$', views.APICallResponseTimeView.as_view()),
    url(r'^api/call_map/', views.APICallMapView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^$', views.LandingPageView.as_view()),
    url(r'^call_volume$', views.CallVolumeView.as_view()),
    url(r'^response_time$', views.ResponseTimeView.as_view()),
    url(r'^calls$', views.CallListView.as_view()),
    url(r'^calls.csv$', views.CallExportView.as_view()),
    url(r'^call_map$', views.MapView.as_view())
]

from django.conf import settings
from importlib import import_module
for app in settings.PLUGINS:
    try:
        mod = import_module('%s.urls' % app)
        # possibly cleanup the after the imported module?
        #  might fuss up the `include(...)` or leave a polluted namespace
    except:
        # cleanup after module import if fails,
        #  maybe you can let the `include(...)` report failures
        pass
    else:
        urlpatterns += mod.urlpatterns