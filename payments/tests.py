from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from providers.models import Provider, ServiceCategory
from bookings.models import Booking
from .models import Payment
import datetime

User = get_user_model()


class PaymentModelTest(TestCase):
    """Test cases for Payment model"""
    
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
            booking_date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
            duration_hours=2.0,
            service_address='123 Main St',
            city='New York',
            postal_code='10001',
            hourly_rate=self.provider.hourly_rate
        )
    
    def test_create_payment(self):
        """Test creating a payment"""
        payment = Payment.objects.create(
            booking=self.booking,
            customer=self.customer,
            amount=self.booking.total_amount,
            payment_method='card'
        )
        
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.amount, 100.00)
