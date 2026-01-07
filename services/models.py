from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from providers.models import Provider, ServiceCategory

User = get_user_model()


class Service(models.Model):
    """Service offered by providers"""
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
    )
    
    PRICING_TYPE_CHOICES = (
        ('hourly', 'Hourly'),
        ('fixed', 'Fixed Price'),
        ('package', 'Package'),
    )
    
    # Relationships
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name='services')
    
    # Service Details
    title = models.CharField(max_length=255)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Pricing
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPE_CHOICES, default='hourly')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Service Info
    duration_minutes = models.PositiveIntegerField(help_text="Estimated service duration in minutes", null=True, blank=True)
    is_remote = models.BooleanField(default=False, help_text="Can service be provided remotely")
    is_onsite = models.BooleanField(default=True, help_text="Can service be provided on-site")
    
    # Availability
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    min_booking_hours = models.PositiveIntegerField(default=24, help_text="Minimum hours before booking")
    max_bookings_per_day = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1)])
    
    # Media
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    
    # Metadata
    views_count = models.PositiveIntegerField(default=0)
    bookings_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.provider.business_name}"
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        from reviews.models import Review
        reviews = Review.objects.filter(provider=self.provider)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ServiceImage(models.Model):
    """Additional images for services"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='services/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'service_images'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"Image for {self.service.title}"


class ServiceFAQ(models.Model):
    """Frequently asked questions about services"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'service_faqs'
        ordering = ['order']
    
    def __str__(self):
        return self.question
