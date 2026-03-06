from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['order', 'title', 'category', 'featured', 'updated_at']
    list_display_links = ['title']
    list_filter = ['category', 'featured']
    search_fields = ['title', 'summary', 'description']
    list_editable = ['order', 'featured']
    ordering = ['order', 'id']
