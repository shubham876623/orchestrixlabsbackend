from rest_framework import serializers
from .models import SiteStat


class SiteStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteStat
        fields = ['total_earnings', 'total_hours', 'total_jobs', 'years_experience', 'jss_score', 'updated_at']
