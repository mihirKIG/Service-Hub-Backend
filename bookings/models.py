from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from providers.models import Provider

User = get_user_model()


class Booking(models.Model):
    """Booking model for service appointments"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    # Relationships
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking Details
    service_title = models.CharField(max_length=255)
    service_description = models.TextField()
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.5)])
    
    # Location
    service_address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    # Pricing
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_bookings'
    )
    
    # Notes
    customer_notes = models.TextField(blank=True)
    provider_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.service_title} - {self.customer.email} - {self.booking_date}"
    
    def save(self, *args, **kwargs):
        # Calculate total amount based on hourly rate and duration
        if self.hourly_rate and self.duration_hours:
            self.total_amount = self.hourly_rate * self.duration_hours
        super().save(*args, **kwargs)


class BookingAttachment(models.Model):
    """Attachments for bookings (images, documents)"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='booking_attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'booking_attachments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking.service_title} - Attachment"
