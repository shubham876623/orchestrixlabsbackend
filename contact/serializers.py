from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    # Honeypot: bots fill "website"; humans never see it. Must stay empty.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True, default='')
    message = serializers.CharField(required=True, allow_blank=False, max_length=5000)
    service = serializers.CharField(required=True, allow_blank=False, max_length=100)

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'service', 'budget', 'message', 'website']

    def validate_name(self, value):
        v = value.strip()
        if len(v) < 2:
            raise serializers.ValidationError('Please enter your full name.')
        if len(v) > 120:
            raise serializers.ValidationError('Name is too long.')
        return v

    def validate_email(self, value):
        v = value.strip().lower()
        if len(v) > 254:
            raise serializers.ValidationError('Email is too long.')
        return v

    def validate_service(self, value):
        v = (value or '').strip()
        if len(v) < 2:
            raise serializers.ValidationError('Please select a service.')
        return v[:100]

    def validate_message(self, value):
        v = (value or '').strip()
        if len(v) < 20:
            raise serializers.ValidationError('Please describe your project in at least a few sentences.')
        return v[:5000]

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError('Spam detected.')
        return ''

    def create(self, validated_data):
        validated_data.pop('website', None)
        return super().create(validated_data)
