from rest_framework import serializers
from .models import Notification, NotificationPreference, EmailLog, SMSLog


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'read_at')


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""
    
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for EmailLog model"""
    
    class Meta:
        model = EmailLog
        fields = '__all__'
        read_only_fields = ('created_at', 'sent_at')


class SMSLogSerializer(serializers.ModelSerializer):
    """Serializer for SMSLog model"""
    
    class Meta:
        model = SMSLog
        fields = '__all__'
        read_only_fields = ('created_at', 'sent_at')
