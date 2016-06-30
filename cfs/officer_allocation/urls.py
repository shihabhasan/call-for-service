"""cfsbackend URL Configuration."""

from django.conf.urls import url

from officer_allocation import views

urlpatterns = [
    url(r'^api/officer_allocation/', views.APIOfficerAllocationView.as_view()),
    url(r'^officer_allocation$', views.OfficerAllocationDashboardView.as_view()),
]