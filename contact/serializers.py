from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'service', 'budget', 'message']

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Please enter your full name.')
        return value.strip()

    def validate_message(self, value):
        return value.strip()
