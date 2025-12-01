from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from providers.models import Provider
from bookings.models import Booking

User = get_user_model()


class Review(models.Model):
    """Review and rating model"""
    
    # Relationships
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    
    # Rating (1-5 scale)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Review Content
    title = models.CharField(max_length=255)
    comment = models.TextField()
    
    # Sub-ratings
    quality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    professionalism_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    punctuality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    value_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    # Status
    is_verified = models.BooleanField(default=True)  # Verified purchase
    is_published = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    
    # Metadata
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ['booking', 'customer']
    
    def __str__(self):
        return f"Review by {self.customer.email} for {self.provider.business_name} - {self.rating} stars"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update provider's average rating
        if is_new or 'rating' in kwargs.get('update_fields', []):
            self.update_provider_rating()
    
    def update_provider_rating(self):
        """Update provider's average rating and review count"""
        reviews = Review.objects.filter(provider=self.provider, is_published=True)
        total_reviews = reviews.count()
        
        if total_reviews > 0:
            average_rating = sum(r.rating for r in reviews) / total_reviews
            self.provider.average_rating = round(average_rating, 2)
            self.provider.total_reviews = total_reviews
            self.provider.save()


class ReviewResponse(models.Model):
    """Provider's response to a review"""
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'review_responses'
    
    def __str__(self):
        return f"Response to review {self.review.id}"


class ReviewImage(models.Model):
    """Images attached to reviews"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='review_images/')
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_images'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Image for review {self.review.id}"


class ReviewHelpful(models.Model):
    """Track users who found reviews helpful"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_helpful'
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.email} found review {self.review.id} helpful"
