from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """Notification model for in-app notifications"""
    
    TYPE_CHOICES = (
        ('booking_created', 'Booking Created'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_completed', 'Booking Completed'),
        ('payment_received', 'Payment Received'),
        ('payment_failed', 'Payment Failed'),
        ('review_received', 'Review Received'),
        ('review_response', 'Review Response'),
        ('message_received', 'Message Received'),
        ('account_verified', 'Account Verified'),
        ('provider_approved', 'Provider Approved'),
        ('provider_rejected', 'Provider Rejected'),
        ('general', 'General Notification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Optional links
    link_url = models.CharField(max_length=500, blank=True)
    
    # Metadata
    data = models.JSONField(blank=True, null=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.email}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class NotificationPreference(models.Model):
    """User notification preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email Notifications
    email_booking_updates = models.BooleanField(default=True)
    email_payment_updates = models.BooleanField(default=True)
    email_review_updates = models.BooleanField(default=True)
    email_messages = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=False)
    
    # SMS Notifications
    sms_booking_updates = models.BooleanField(default=False)
    sms_payment_updates = models.BooleanField(default=False)
    
    # Push Notifications
    push_booking_updates = models.BooleanField(default=True)
    push_payment_updates = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    
    # In-app Notifications
    inapp_all = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Notification Preferences for {self.user.email}"


class EmailLog(models.Model):
    """Log of sent emails"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs', null=True, blank=True)
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email to {self.recipient_email} - {self.status}"


class SMSLog(models.Model):
    """Log of sent SMS messages"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sms_logs', null=True, blank=True)
    recipient_phone = models.CharField(max_length=15)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sms_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SMS to {self.recipient_phone} - {self.status}"
