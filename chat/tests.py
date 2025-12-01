from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


class ChatModelTest(TestCase):
    """Test cases for Chat models"""
    
    def setUp(self):
        self.customer = User.objects.create_user(
            email='customer@example.com',
            username='customer',
            password='testpass123'
        )
        self.provider = User.objects.create_user(
            email='provider@example.com',
            username='provider',
            password='testpass123',
            user_type='provider'
        )
    
    def test_create_chatroom(self):
        """Test creating a chatroom"""
        chatroom = ChatRoom.objects.create(
            customer=self.customer,
            provider=self.provider
        )
        
        self.assertTrue(chatroom.is_active)
        self.assertEqual(str(chatroom), f"Chat: {self.customer.email} - {self.provider.email}")
    
    def test_create_message(self):
        """Test creating a message"""
        chatroom = ChatRoom.objects.create(
            customer=self.customer,
            provider=self.provider
        )
        
        message = Message.objects.create(
            chatroom=chatroom,
            sender=self.customer,
            content='Hello, I need your service'
        )
        
        self.assertEqual(message.message_type, 'text')
        self.assertFalse(message.is_read)
