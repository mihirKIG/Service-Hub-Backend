from django.urls import path
from .views import (
    ChatRoomListView,
    ChatRoomDetailView,
    ChatRoomCreateView,
    MessageListView,
    MessageCreateView,
    unread_messages_count,
    mark_messages_read
)

urlpatterns = [
    # Chat Rooms
    path('rooms/', ChatRoomListView.as_view(), name='chatroom-list'),
    path('rooms/create/', ChatRoomCreateView.as_view(), name='chatroom-create'),
    path('rooms/<int:pk>/', ChatRoomDetailView.as_view(), name='chatroom-detail'),
    
    # Messages
    path('rooms/<int:chatroom_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('rooms/<int:chatroom_id>/messages/send/', MessageCreateView.as_view(), name='message-create'),
    path('rooms/<int:chatroom_id>/mark-read/', mark_messages_read, name='messages-mark-read'),
    
    # Unread Count
    path('unread-count/', unread_messages_count, name='unread-messages-count'),
]
