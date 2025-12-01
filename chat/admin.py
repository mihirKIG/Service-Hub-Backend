from django.contrib import admin
from .models import ChatRoom, Message, TypingStatus


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'provider', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('customer__email', 'provider__email')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chatroom', 'sender', 'message_type', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('sender__email', 'content')


@admin.register(TypingStatus)
class TypingStatusAdmin(admin.ModelAdmin):
    list_display = ('chatroom', 'user', 'is_typing', 'updated_at')
