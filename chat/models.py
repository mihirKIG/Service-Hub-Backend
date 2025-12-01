from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoom(models.Model):
    """Chat room between customer and provider"""
    
    # Participants
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_chatrooms')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_chatrooms')
    
    # Metadata
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='chatroom')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-updated_at']
        unique_together = ['customer', 'provider']
    
    def __str__(self):
        return f"Chat: {self.customer.email} - {self.provider.email}"
    
    @property
    def room_name(self):
        """Generate unique room name for WebSocket"""
        return f"chat_{self.id}"


class Message(models.Model):
    """Chat message model"""
    
    MESSAGE_TYPE_CHOICES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    )
    
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.email} in {self.chatroom.id}"
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class TypingStatus(models.Model):
    """Track typing status in chat rooms"""
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='typing_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'typing_status'
        unique_together = ['chatroom', 'user']
    
    def __str__(self):
        return f"{self.user.email} typing in {self.chatroom.id}"
