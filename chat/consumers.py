from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for real-time chat"""
    
    async def connect(self):
        self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
        self.room_group_name = f'chat_{self.chatroom_id}'
        self.user = self.scope['user']
        
        # Verify user has access to this chatroom
        has_access = await self.verify_chatroom_access()
        
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send user connected notification
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'status': 'online'
            }
        )
    
    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'status': 'offline'
                }
            )
            
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive_json(self, content):
        message_type = content.get('type', 'message')
        
        if message_type == 'message':
            # Save message to database
            message = await self.save_message(content)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': await self.message_to_dict(message)
                }
            )
        
        elif message_type == 'typing':
            # Broadcast typing status
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'user_id': self.user.id,
                    'is_typing': content.get('is_typing', False)
                }
            )
    
    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send_json({
            'type': 'message',
            'message': event['message']
        })
    
    async def typing_status(self, event):
        """Send typing status to WebSocket"""
        # Don't send typing status back to the sender
        if event['user_id'] != self.user.id:
            await self.send_json({
                'type': 'typing',
                'user_id': event['user_id'],
                'is_typing': event['is_typing']
            })
    
    async def user_status(self, event):
        """Send user online/offline status"""
        if event['user_id'] != self.user.id:
            await self.send_json({
                'type': 'user_status',
                'user_id': event['user_id'],
                'status': event['status']
            })
    
    @database_sync_to_async
    def verify_chatroom_access(self):
        """Verify user has access to chatroom"""
        from .models import ChatRoom
        from django.db.models import Q
        
        try:
            chatroom = ChatRoom.objects.get(
                id=self.chatroom_id,
                is_active=True
            )
            return (chatroom.customer == self.user or 
                    chatroom.provider == self.user)
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Save message to database"""
        from .models import Message, ChatRoom
        
        chatroom = ChatRoom.objects.get(id=self.chatroom_id)
        message = Message.objects.create(
            chatroom=chatroom,
            sender=self.user,
            message_type=content.get('message_type', 'text'),
            content=content.get('content', '')
        )
        return message
    
    @database_sync_to_async
    def message_to_dict(self, message):
        """Convert message to dictionary"""
        return {
            'id': message.id,
            'sender_id': message.sender.id,
            'sender_name': message.sender.full_name,
            'message_type': message.message_type,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read
        }
