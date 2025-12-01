from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Max
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from .serializers import (
    ChatRoomSerializer,
    ChatRoomCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer
)

User = get_user_model()


class ChatRoomListView(generics.ListAPIView):
    """List all chat rooms for authenticated user"""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(customer=user) | Q(provider=user),
            is_active=True
        ).annotate(
            last_message_time=Max('messages__created_at')
        ).order_by('-last_message_time')


class ChatRoomDetailView(generics.RetrieveAPIView):
    """Retrieve chat room details"""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(customer=user) | Q(provider=user)
        )


class ChatRoomCreateView(generics.CreateAPIView):
    """Create or get existing chat room"""
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        other_user = User.objects.get(id=serializer.validated_data['other_user_id'])
        current_user = request.user
        
        # Determine who is customer and who is provider
        if hasattr(current_user, 'provider_profile'):
            provider = current_user
            customer = other_user
        elif hasattr(other_user, 'provider_profile'):
            provider = other_user
            customer = current_user
        else:
            return Response(
                {'error': 'At least one participant must be a provider'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create chatroom
        chatroom, created = ChatRoom.objects.get_or_create(
            customer=customer,
            provider=provider
        )
        
        return Response(
            ChatRoomSerializer(chatroom, context={'request': request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class MessageListView(generics.ListAPIView):
    """List messages in a chat room"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        chatroom_id = self.kwargs.get('chatroom_id')
        user = self.request.user
        
        # Verify user has access to this chatroom
        chatroom = ChatRoom.objects.filter(
            id=chatroom_id
        ).filter(
            Q(customer=user) | Q(provider=user)
        ).first()
        
        if not chatroom:
            return Message.objects.none()
        
        # Mark all messages as read for the current user
        Message.objects.filter(
            chatroom=chatroom,
            is_read=False
        ).exclude(sender=user).update(is_read=True)
        
        return Message.objects.filter(
            chatroom_id=chatroom_id,
            is_deleted=False
        )


class MessageCreateView(generics.CreateAPIView):
    """Send a message in a chat room"""
    serializer_class = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        chatroom_id = kwargs.get('chatroom_id')
        
        # Verify user has access to this chatroom
        chatroom = ChatRoom.objects.filter(
            id=chatroom_id
        ).filter(
            Q(customer=request.user) | Q(provider=request.user)
        ).first()
        
        if not chatroom:
            return Response(
                {'error': 'Chat room not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = Message.objects.create(
            chatroom=chatroom,
            sender=request.user,
            **serializer.validated_data
        )
        
        # Update chatroom timestamp
        chatroom.save()
        
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_messages_count(request):
    """Get total unread messages count"""
    user = request.user
    
    # Get all chatrooms for user
    chatrooms = ChatRoom.objects.filter(
        Q(customer=user) | Q(provider=user),
        is_active=True
    )
    
    # Count unread messages
    unread_count = Message.objects.filter(
        chatroom__in=chatrooms,
        is_read=False,
        is_deleted=False
    ).exclude(sender=user).count()
    
    return Response({'unread_count': unread_count})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_messages_read(request, chatroom_id):
    """Mark all messages in a chatroom as read"""
    user = request.user
    
    # Verify user has access to this chatroom
    chatroom = ChatRoom.objects.filter(
        id=chatroom_id
    ).filter(
        Q(customer=user) | Q(provider=user)
    ).first()
    
    if not chatroom:
        return Response(
            {'error': 'Chat room not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    from django.utils import timezone
    count = Message.objects.filter(
        chatroom=chatroom,
        is_read=False
    ).exclude(sender=user).update(is_read=True, read_at=timezone.now())
    
    return Response(
        {'message': f'{count} messages marked as read'},
        status=status.HTTP_200_OK
    )
