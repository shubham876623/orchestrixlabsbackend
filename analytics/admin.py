from django.contrib import admin
from .models import PageView, SiteStat


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['path', 'ip_address', 'timestamp']
    list_filter = ['path']
    readonly_fields = ['path', 'referrer', 'ip_address', 'user_agent', 'timestamp']
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False


@admin.register(SiteStat)
class SiteStatAdmin(admin.ModelAdmin):
    list_display = ['total_earnings', 'total_hours', 'total_jobs', 'years_experience', 'jss_score', 'updated_at']

    def has_add_permission(self, request):
        # Only allow editing the existing singleton row
        return not SiteStat.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
