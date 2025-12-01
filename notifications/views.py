from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationListView(generics.ListAPIView):
    """List all notifications for authenticated user"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(user=user, is_deleted=False)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Filter by type
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset


class NotificationDetailView(generics.RetrieveAPIView):
    """Retrieve notification details"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_deleted=False)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Automatically mark as read when retrieved
        instance.mark_as_read()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.mark_as_read()
        return Response(
            {'message': 'Notification marked as read'},
            status=status.HTTP_200_OK
        )
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read"""
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False,
        is_deleted=False
    )
    
    count = notifications.update(is_read=True, read_at=timezone.now())
    
    return Response(
        {'message': f'{count} notifications marked as read'},
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_notification(request, pk):
    """Delete a notification (soft delete)"""
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_deleted = True
        notification.save()
        return Response(
            {'message': 'Notification deleted'},
            status=status.HTTP_200_OK
        )
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_all_notifications(request):
    """Clear all notifications (soft delete)"""
    count = Notification.objects.filter(
        user=request.user,
        is_deleted=False
    ).update(is_deleted=True)
    
    return Response(
        {'message': f'{count} notifications cleared'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    """Get count of unread notifications"""
    count = Notification.objects.filter(
        user=request.user,
        is_read=False,
        is_deleted=False
    ).count()
    
    return Response({'unread_count': count})


# Notification Preferences
class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """Get and update notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Get or create notification preferences for user
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences


# Helper function to create notifications
def create_notification(user, notification_type, title, message, link_url='', data=None):
    """
    Create a notification for a user
    
    Args:
        user: User object
        notification_type: Type of notification from TYPE_CHOICES
        title: Notification title
        message: Notification message
        link_url: Optional URL link
        data: Optional metadata dictionary
    
    Returns:
        Notification object
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link_url=link_url,
        data=data
    )
    return notification
