from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import ServiceCategory, Provider

User = get_user_model()


class ProviderModelTest(TestCase):
    """Test cases for Provider model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='provider@example.com',
            username='provider',
            password='testpass123',
            user_type='provider'
        )
        self.category = ServiceCategory.objects.create(name='Plumbing')
    
    def test_create_provider(self):
        """Test creating a provider"""
        provider = Provider.objects.create(
            user=self.user,
            business_name='Test Plumbing Services',
            hourly_rate=50.00,
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001'
        )
        provider.categories.add(self.category)
        
        self.assertEqual(provider.business_name, 'Test Plumbing Services')
        self.assertEqual(provider.status, 'pending')
        self.assertTrue(provider.is_available)


class ProviderAPITest(APITestCase):
    """Test cases for Provider API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='provider@example.com',
            username='provider',
            password='testpass123',
            user_type='provider'
        )
        self.category = ServiceCategory.objects.create(name='Plumbing')
    
    def test_create_provider_profile(self):
        """Test creating provider profile"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'business_name': 'Test Services',
            'bio': 'Professional services',
            'category_ids': [self.category.id],
            'experience_years': 5,
            'hourly_rate': 50.00,
            'city': 'New York',
            'state': 'NY',
            'country': 'USA',
            'postal_code': '10001'
        }
        
        response = self.client.post('/api/providers/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_providers(self):
        """Test listing providers"""
        provider = Provider.objects.create(
            user=self.user,
            business_name='Test Services',
            hourly_rate=50.00,
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001',
            status='approved'
        )
        
        response = self.client.get('/api/providers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
