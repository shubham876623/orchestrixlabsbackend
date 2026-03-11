from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=False, allow_blank=True, default='', max_length=5000)

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'service', 'budget', 'message']

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

    def validate_message(self, value):
        return value.strip()[:5000]
