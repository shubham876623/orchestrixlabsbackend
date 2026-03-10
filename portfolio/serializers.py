from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'category', 'status', 'summary', 'description',
            'tech', 'highlights', 'impact', 'featured', 'order',
            'client_name', 'rating', 'review', 'tags',
            'project_value', 'hours_worked', 'price_type', 'start_date', 'completion_date',
            'job_description', 'deliverables', 'live_url', 'upwork_url', 'images',
            'created_at', 'updated_at',
        ]


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'title', 'category', 'status', 'summary', 'description',
            'tech', 'highlights', 'impact', 'featured', 'order',
            'client_name', 'rating', 'review', 'tags',
            'project_value', 'hours_worked', 'price_type', 'start_date', 'completion_date',
            'job_description', 'deliverables', 'live_url', 'upwork_url', 'images',
        ]
