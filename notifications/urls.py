from django.urls import path
from .views import (
    NotificationListView,
    NotificationDetailView,
    NotificationPreferenceView,
    mark_notification_read,
    mark_all_read,
    delete_notification,
    clear_all_notifications,
    unread_count
)

urlpatterns = [
    # Notifications
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', unread_count, name='notification-unread-count'),
    path('mark-all-read/', mark_all_read, name='notification-mark-all-read'),
    path('clear-all/', clear_all_notifications, name='notification-clear-all'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/mark-read/', mark_notification_read, name='notification-mark-read'),
    path('<int:pk>/delete/', delete_notification, name='notification-delete'),
    
    # Preferences
    path('preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),
]
