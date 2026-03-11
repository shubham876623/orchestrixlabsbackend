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
    # Public CMS
    TestimonialsPublicView,
    FAQPublicView,
    InsightBadgesPublicView,
    SiteContentPublicView,
    # Dashboard CMS CRUD
    DashboardTestimonialsView,
    DashboardTestimonialDetailView,
    DashboardFAQsView,
    DashboardFAQDetailView,
    DashboardBadgesView,
    DashboardBadgeDetailView,
    DashboardSiteContentView,
)

urlpatterns = [
    path('track/', TrackPageView.as_view(), name='track-pageview'),
    path('site-stats/', SiteStatView.as_view(), name='site-stats'),
    # Public CMS endpoints
    path('testimonials/', TestimonialsPublicView.as_view(), name='testimonials'),
    path('faqs/', FAQPublicView.as_view(), name='faqs'),
    path('badges/', InsightBadgesPublicView.as_view(), name='badges'),
    path('site-content/', SiteContentPublicView.as_view(), name='site-content'),
    # Dashboard
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/contacts/', DashboardContactsView.as_view(), name='dashboard-contacts'),
    path('dashboard/contacts/<int:pk>/', DashboardContactUpdateView.as_view(), name='dashboard-contact-update'),
    path('dashboard/site-stats/', DashboardSiteStatUpdateView.as_view(), name='dashboard-site-stats'),
    path('dashboard/projects/', DashboardProjectsView.as_view(), name='dashboard-projects'),
    path('dashboard/projects/<int:pk>/', DashboardProjectDetailView.as_view(), name='dashboard-project-detail'),
    # Dashboard CMS CRUD
    path('dashboard/testimonials/', DashboardTestimonialsView.as_view(), name='dashboard-testimonials'),
    path('dashboard/testimonials/<int:pk>/', DashboardTestimonialDetailView.as_view(), name='dashboard-testimonial-detail'),
    path('dashboard/faqs/', DashboardFAQsView.as_view(), name='dashboard-faqs'),
    path('dashboard/faqs/<int:pk>/', DashboardFAQDetailView.as_view(), name='dashboard-faq-detail'),
    path('dashboard/badges/', DashboardBadgesView.as_view(), name='dashboard-badges'),
    path('dashboard/badges/<int:pk>/', DashboardBadgeDetailView.as_view(), name='dashboard-badge-detail'),
    path('dashboard/site-content/', DashboardSiteContentView.as_view(), name='dashboard-site-content'),
]
