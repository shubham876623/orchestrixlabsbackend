from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service', 'budget', 'status', 'notify_status', 'created_at']
    list_filter = ['status', 'notify_status', 'service', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['ip_address', 'created_at', 'notify_status', 'notify_error']
    list_editable = ['status']
    ordering = ['-created_at']
