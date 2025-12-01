from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from providers.models import Provider, ServiceCategory
from .models import Booking
import datetime

User = get_user_model()


class BookingModelTest(TestCase):
    """Test cases for Booking model"""
    
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
        self.category = ServiceCategory.objects.create(name='Plumbing')
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
    
    def test_create_booking(self):
        """Test creating a booking"""
        booking = Booking.objects.create(
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
        
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.total_amount, 100.00)


class BookingAPITest(APITestCase):
    """Test cases for Booking API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
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
        self.category = ServiceCategory.objects.create(name='Plumbing')
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
    
    def test_create_booking(self):
        """Test creating a booking via API"""
        self.client.force_authenticate(user=self.customer)
        
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        data = {
            'provider_id': self.provider.id,
            'service_title': 'Fix Leak',
            'service_description': 'Need to fix kitchen sink leak',
            'booking_date': tomorrow.isoformat(),
            'start_time': '10:00:00',
            'end_time': '12:00:00',
            'duration_hours': 2.0,
            'service_address': '123 Main St',
            'city': 'New York',
            'postal_code': '10001'
        }
        
        response = self.client.post('/api/bookings/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
