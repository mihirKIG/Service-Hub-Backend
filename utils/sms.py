"""
SMS utility functions using Twilio
"""
from django.conf import settings
from notifications.models import SMSLog
from django.utils import timezone


def send_sms(phone_number, message, user=None):
    """
    Send SMS using Twilio
    
    Args:
        phone_number: Recipient phone number
        message: SMS message content
        user: Optional User object
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        from twilio.rest import Client
        
        # Initialize Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Send SMS
        sms = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        # Log SMS
        SMSLog.objects.create(
            user=user,
            recipient_phone=phone_number,
            message=message,
            status='sent',
            sent_at=timezone.now()
        )
        
        return True
    
    except Exception as e:
        # Log failed SMS
        SMSLog.objects.create(
            user=user,
            recipient_phone=phone_number,
            message=message,
            status='failed',
            error_message=str(e)
        )
        
        return False


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
    """Send OTP verification SMS"""
    message = f"Your ServiceHub verification code is: {otp_code}. Valid for 10 minutes."
    return send_sms(phone_number, message, user)
