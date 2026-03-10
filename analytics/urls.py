from django.urls import path
from .views import (
    TrackPageView,
    SiteStatView,
    DashboardStatsView,
    DashboardContactsView,
    DashboardContactUpdateView,
    DashboardSiteStatUpdateView,
    DashboardProjectsView,
    DashboardProjectDetailView,
)

urlpatterns = [
    path('track/', TrackPageView.as_view(), name='track-pageview'),
    path('site-stats/', SiteStatView.as_view(), name='site-stats'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/contacts/', DashboardContactsView.as_view(), name='dashboard-contacts'),
    path('dashboard/contacts/<int:pk>/', DashboardContactUpdateView.as_view(), name='dashboard-contact-update'),
    path('dashboard/site-stats/', DashboardSiteStatUpdateView.as_view(), name='dashboard-site-stats'),
    path('dashboard/projects/', DashboardProjectsView.as_view(), name='dashboard-projects'),
    path('dashboard/projects/<int:pk>/', DashboardProjectDetailView.as_view(), name='dashboard-project-detail'),
]
