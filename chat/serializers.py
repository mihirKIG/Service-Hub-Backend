from rest_framework import serializers
from .models import ChatRoom, Message
from users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('sender', 'chatroom', 'created_at', 'read_at')


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    
    class Meta:
        model = Message
        fields = ('message_type', 'content', 'file')


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for ChatRoom model"""
    customer = UserSerializer(read_only=True)
    provider = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = '__all__'
        read_only_fields = ('customer', 'provider', 'created_at', 'updated_at')
    
    def get_last_message(self, obj):
        last_message = obj.messages.filter(is_deleted=False).last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user
        return obj.messages.filter(is_read=False, is_deleted=False).exclude(sender=user).count()


class ChatRoomCreateSerializer(serializers.Serializer):
    """Serializer for creating chat rooms"""
    other_user_id = serializers.IntegerField()
    
    def validate_other_user_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        # Cannot create chatroom with yourself
        if user == self.context['request'].user:
            raise serializers.ValidationError("Cannot create chatroom with yourself")
        
        return value
