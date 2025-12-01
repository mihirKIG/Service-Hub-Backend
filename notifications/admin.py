from django.contrib import admin
from .models import Notification, NotificationPreference, EmailLog, SMSLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'is_deleted', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_deleted', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_booking_updates', 'sms_booking_updates', 'push_booking_updates')
    search_fields = ('user__email',)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_email', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('recipient_email', 'subject')


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_phone', 'status', 'sent_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('recipient_phone',)
