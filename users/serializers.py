from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.cache import cache
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from utils.sms import verify_otp
from utils.sms import send_otp
import random
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - Clean API response"""
    
    class Meta:
        model = User
        fields = (
            'id', 'phone', 'google_uid', 'is_verified', 
            'first_name', 'last_name', 'email', 'profile_picture',
            'date_joined', 'full_name'
        )
        read_only_fields = ('id', 'is_verified', 'date_joined', 'full_name')


class SendOTPSerializer(serializers.Serializer):
    """Serializer for sending OTP to phone"""
    phone = serializers.CharField(
        max_length=20,
        help_text='Phone number with country code (E.164 format, e.g., +1234567890)'
    )
    
    def validate_phone(self, value):
        # E.164 phone validation
        if not re.match(r'^\+?[1-9]\d{1,14}$', value):
            raise serializers.ValidationError(
                "Enter a valid phone number with country code (E.164 format)"
            )
        return value
    
    def save(self):
        """Generate OTP, cache it, and send via BulkSMSBD"""
        
        
        phone = self.validated_data['phone']
        
        # Generate and send OTP via BulkSMSBD
        otp, expires_in = send_otp(phone)
        
        # In DEBUG mode, return OTP for testing
        if settings.DEBUG:
            return {
                'success': True,
                'message': 'OTP sent successfully',
                'phone': phone,
                'otp': otp,  # Only visible in DEBUG mode
                'expires_in_seconds': expires_in
            }
        
        # Production mode: Don't return OTP
        return {
            'success': True,
            'message': 'OTP sent to your phone number',
            'phone': phone,
            'expires_in_seconds': expires_in
        }


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP and logging in/registering user"""
    phone = serializers.CharField(max_length=20)
    otp = serializers.CharField(min_length=6, max_length=6)
    
    # Optional fields for new user registration
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    
    def validate(self, attrs):
        
        
        phone = attrs.get('phone')
        otp = attrs.get('otp')
        
        # Verify OTP using utility function
        is_valid, error_message = verify_otp(phone, otp)
        
        if not is_valid:
            raise serializers.ValidationError({
                "otp": error_message
            })
        
        return attrs


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Firebase Google Sign-In authentication"""
    uid = serializers.CharField(required=True, help_text='Firebase user UID')
    email = serializers.EmailField(required=True)
    displayName = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    photoURL = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    
    def validate(self, attrs):
        """Validate and extract user info from Firebase"""
        google_uid = attrs.get('uid')
        email = attrs.get('email')
        display_name = attrs.get('displayName', '')
        photo_url = attrs.get('photoURL')
        
        if not google_uid:
            raise serializers.ValidationError({'uid': 'Firebase UID is required'})
        
        if not email:
            raise serializers.ValidationError({'email': 'Email is required'})
        
        # Parse display name into first and last name
        name_parts = display_name.split(' ', 1) if display_name else ['', '']
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Store verified info in context for later use
        self.context['google_user_info'] = {
            'google_uid': google_uid,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'profile_picture': photo_url,
            'email_verified': True  # Firebase emails are verified
        }
        
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_picture')
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True, 'allow_null': True}
        }
