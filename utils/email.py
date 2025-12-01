"""
Email utility functions
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from notifications.models import EmailLog
from django.utils import timezone


def send_email(subject, message, recipient_list, html_message=None, user=None):
    """
    Send email
    
    Args:
        subject: Email subject
        message: Plain text message
        recipient_list: List of recipient email addresses
        html_message: Optional HTML message
        user: Optional User object
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        
        # Log email
        for recipient in recipient_list:
            EmailLog.objects.create(
                user=user,
                recipient_email=recipient,
                subject=subject,
                body=message,
                status='sent',
                sent_at=timezone.now()
            )
        
        return True
    
    except Exception as e:
        # Log failed email
        for recipient in recipient_list:
            EmailLog.objects.create(
                user=user,
                recipient_email=recipient,
                subject=subject,
                body=message,
                status='failed',
                error_message=str(e)
            )
        
        return False


def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = 'Welcome to ServiceHub!'
    message = f"""
    Hi {user.first_name or user.username},
    
    Welcome to ServiceHub! We're excited to have you on board.
    
    {'As a service provider, you can now start offering your services and connecting with customers.' if user.user_type == 'provider' else 'You can now browse and book services from verified providers.'}
    
    Get started by completing your profile and exploring available services.
    
    Best regards,
    The ServiceHub Team
    """
    
    return send_email(
        subject=subject,
        message=message.strip(),
        recipient_list=[user.email],
        user=user
    )


def send_booking_confirmation_email(booking):
    """Send booking confirmation email"""
    subject = f'Booking Confirmed - {booking.service_title}'
    message = f"""
    Hi {booking.customer.first_name or booking.customer.username},
    
    Your booking has been confirmed!
    
    Service: {booking.service_title}
    Provider: {booking.provider.business_name}
    Date: {booking.booking_date}
    Time: {booking.start_time} - {booking.end_time}
    Location: {booking.service_address}
    Total Amount: ${booking.total_amount}
    
    If you have any questions, please contact the provider through our messaging system.
    
    Best regards,
    ServiceHub Team
    """
    
    return send_email(
        subject=subject,
        message=message.strip(),
        recipient_list=[booking.customer.email],
        user=booking.customer
    )


def send_booking_notification_to_provider(booking):
    """Send new booking notification to provider"""
    subject = f'New Booking Request - {booking.service_title}'
    message = f"""
    Hi {booking.provider.user.first_name or booking.provider.business_name},
    
    You have received a new booking request!
    
    Service: {booking.service_title}
    Customer: {booking.customer.full_name}
    Date: {booking.booking_date}
    Time: {booking.start_time} - {booking.end_time}
    Location: {booking.service_address}
    Amount: ${booking.total_amount}
    
    Please log in to your account to review and confirm the booking.
    
    Best regards,
    ServiceHub Team
    """
    
    return send_email(
        subject=subject,
        message=message.strip(),
        recipient_list=[booking.provider.user.email],
        user=booking.provider.user
    )


def send_payment_receipt_email(payment):
    """Send payment receipt email"""
    subject = f'Payment Receipt - ${payment.amount}'
    message = f"""
    Hi {payment.customer.first_name or payment.customer.username},
    
    Thank you for your payment!
    
    Transaction ID: {payment.transaction_id}
    Amount: ${payment.amount} {payment.currency}
    Payment Method: {payment.get_payment_method_display()}
    Date: {payment.completed_at}
    
    Service: {payment.booking.service_title}
    Provider: {payment.booking.provider.business_name}
    
    This receipt confirms your payment has been processed successfully.
    
    Best regards,
    ServiceHub Team
    """
    
    return send_email(
        subject=subject,
        message=message.strip(),
        recipient_list=[payment.customer.email],
        user=payment.customer
    )


def send_review_notification_email(review):
    """Send review notification to provider"""
    subject = f'New Review Received - {review.rating} Stars'
    message = f"""
    Hi {review.provider.user.first_name or review.provider.business_name},
    
    You have received a new review!
    
    Rating: {review.rating}/5 stars
    From: {review.customer.full_name}
    Service: {review.booking.service_title}
    
    Review: {review.comment}
    
    You can respond to this review by logging into your account.
    
    Best regards,
    ServiceHub Team
    """
    
    return send_email(
        subject=subject,
        message=message.strip(),
        recipient_list=[review.provider.user.email],
        user=review.provider.user
    )


def send_password_reset_email(user, reset_link):
    """Send password reset email"""
    subject = 'Password Reset Request'
    message = f"""
    Hi {user.first_name or user.username},
    
    You requested to reset your password for your ServiceHub account.
    
    Click the link below to reset your password:
    {reset_link}
    
    This link will expire in 24 hours.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    ServiceHub Team
    """
    
    return send_email(
        subject=subject,
        message=message.strip(),
        recipient_list=[user.email],
        user=user
    )
