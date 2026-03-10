from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'category', 'status', 'summary', 'description',
            'tech', 'highlights', 'impact', 'featured', 'order',
            'client_name', 'rating', 'review', 'tags',
            'project_value', 'hours_worked', 'start_date', 'completion_date',
            'created_at', 'updated_at',
        ]


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'title', 'category', 'status', 'summary', 'description',
            'tech', 'highlights', 'impact', 'featured', 'order',
            'client_name', 'rating', 'review', 'tags',
            'project_value', 'hours_worked', 'start_date', 'completion_date',
        ]
