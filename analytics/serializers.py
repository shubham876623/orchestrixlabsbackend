from rest_framework import serializers
from .models import SiteStat, Testimonial, FAQ, InsightBadge, SiteContent


class SiteStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteStat
        fields = ['total_earnings', 'total_hours', 'total_jobs', 'years_experience', 'jss_score', 'updated_at']


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            'id', 'client_name', 'client_role', 'rating', 'quote',
            'tags', 'source', 'featured', 'order', 'is_active', 'created_at',
        ]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'order', 'is_active', 'created_at']


class InsightBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsightBadge
        fields = ['id', 'label', 'count', 'order', 'is_active']


class SiteContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteContent
        fields = [
            'hero_headline', 'hero_subheadline', 'hero_cta_primary', 'hero_cta_secondary',
            'about_headline', 'about_story', 'about_values',
            'contact_email', 'contact_linkedin', 'contact_github', 'contact_upwork',
            'services_headline', 'services_data', 'process_steps',
            'site_name', 'site_tagline', 'updated_at',
        ]
