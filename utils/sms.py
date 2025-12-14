"""
SMS utility functions using BulkSMS BD
"""
import requests
import urllib.parse
import random
from django.conf import settings
from django.core.cache import cache
from notifications.models import SMSLog
from django.utils import timezone


def normalize_phone(phone_number):
    """
    Normalize phone number to Bangladesh local format (without country code)
    
    Args:
        phone_number: Phone in any format (+8801719159900, 8801719159900, 01719159900)
    
    Returns:
        str: Normalized phone (01719159900)
    """
    # Remove country code if present
    if phone_number.startswith('+88'):
        phone_number = phone_number[3:]
    elif phone_number.startswith('88'):
        phone_number = phone_number[2:]
    
    # Remove any non-digit characters
    phone_number = ''.join(filter(str.isdigit, phone_number))
    
    return phone_number


def send_sms(phone_number, message, user=None):
    """
    Send SMS using BulkSMS BD API
    
    Args:
        phone_number: Recipient phone number (any format)
        message: SMS message content
        user: Optional User object
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Normalize phone number
        normalized_phone = normalize_phone(phone_number)
        
        # Build API URL
        params = {
            'api_key': settings.BULKSMS_API_KEY,
            'type': 'text',
            'number': normalized_phone,
            'senderid': settings.BULKSMS_SENDER_ID,
            'message': message
        }
        
        url = f"{settings.BULKSMS_API_URL}?{urllib.parse.urlencode(params)}"
        
        # Send SMS via HTTP GET
        response = requests.get(url, timeout=10)
        
        # Check if successful (BulkSMS BD returns 200 on success)
        if response.status_code == 200:
            # Log SMS
            try:
                SMSLog.objects.create(
                    user=user,
                    recipient_phone=normalized_phone,
                    message=message,
                    status='sent',
                    sent_at=timezone.now()
                )
            except Exception:
                pass  # Ignore logging errors
            
            return True
        else:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
    
    except Exception as e:
        # Log failed SMS
        try:
            SMSLog.objects.create(
                user=user,
                recipient_phone=normalize_phone(phone_number),
                message=message,
                status='failed',
                error_message=str(e)
            )
        except Exception:
            pass  # Ignore logging errors
        
        return False


def send_otp(phone_number):
    """
    Generate OTP, cache it, and send via SMS
    
    Args:
        phone_number: Recipient phone number (any format)
    
    Returns:
        tuple: (otp, expires_in_seconds)
    """
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP in cache for 2 minutes (120 seconds)
    cache_key = f'otp_{phone_number}'
    cache.set(cache_key, otp, timeout=120)
    
    # Prepare SMS message
    message = f'Your ServiceHub verification code is: {otp}. Valid for 2 minutes.'
    
    # Send OTP via SMS
    send_sms(phone_number, message)
    
    return otp, 120


def verify_otp(phone_number, otp):
    """
    Verify OTP from cache
    
    Args:
        phone_number: Phone number that received OTP
        otp: OTP code to verify
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Retrieve OTP from cache
    cache_key = f'otp_{phone_number}'
    cached_otp = cache.get(cache_key)
    
    if not cached_otp:
        return False, "OTP has expired or does not exist. Please request a new one."
    
    if cached_otp != otp:
        return False, "Invalid OTP. Please check and try again."
    
    # OTP is valid - delete it from cache (single use)
    cache.delete(cache_key)
    
    return True, None


def send_booking_confirmation_sms(booking):
    """Send booking confirmation SMS to customer"""
    message = f"""
    Booking Confirmed!
    Service: {booking.service_title}
    Date: {booking.booking_date}
    Time: {booking.start_time}
    Provider: {booking.provider.business_name}
    
    Thank you for using ServiceHub!
    """
    
    if booking.customer.phone_number:
        return send_sms(
            booking.customer.phone_number,
            message.strip(),
            booking.customer
        )
    return False


def send_booking_reminder_sms(booking):
    """Send booking reminder SMS"""
    message = f"""
    Reminder: You have an upcoming service appointment
    Service: {booking.service_title}
    Date: {booking.booking_date}
    Time: {booking.start_time}
    
    ServiceHub
    """
    
    if booking.customer.phone_number:
        return send_sms(
            booking.customer.phone_number,
            message.strip(),
            booking.customer
        )
    return False


def send_otp_sms(phone_number, otp_code, user=None):
    """
    Deprecated: Use send_otp() instead
    Send OTP verification SMS
    """
    message = f"Your ServiceHub verification code is: {otp_code}. Valid for 2 minutes."
    return send_sms(phone_number, message, user)

