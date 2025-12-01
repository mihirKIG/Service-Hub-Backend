from django.test import TestCase
from django.contrib.auth import get_user_model
from providers.models import Provider, ServiceCategory
from bookings.models import Booking
from .models import Review
import datetime

User = get_user_model()


class ReviewModelTest(TestCase):
    """Test cases for Review model"""
    
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            username='customer',
            password='testpass123'
        )
        self.provider_user = User.objects.create_user(
            email='provider@example.com',
            username='provider',
            password='testpass123',
            user_type='provider'
        )
        self.provider = Provider.objects.create(
            user=self.provider_user,
            business_name='Test Services',
            hourly_rate=50.00,
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001',
            status='approved'
        )
        self.booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service_title='Fix Leak',
            service_description='Need to fix kitchen sink leak',
            booking_date=datetime.date.today(),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
            duration_hours=2.0,
            service_address='123 Main St',
            city='New York',
            postal_code='10001',
            hourly_rate=self.provider.hourly_rate,
            status='completed'
        )
    
    def test_create_review(self):
        """Test creating a review"""
        review = Review.objects.create(
            booking=self.booking,
            provider=self.provider,
            customer=self.customer,
            rating=5,
            title='Excellent Service',
            comment='Very professional and punctual'
        )
        
        self.assertEqual(review.rating, 5)
        self.assertTrue(review.is_verified)
        self.assertTrue(review.is_published)
