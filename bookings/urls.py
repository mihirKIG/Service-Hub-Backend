from django.urls import path
from .views import (
    BookingListView,
    BookingDetailView,
    BookingCreateView,
    BookingUpdateView,
    BookingCancelView,
    BookingAttachmentListView,
    BookingAttachmentDetailView,
    upcoming_bookings,
    booking_stats
)

urlpatterns = [
    # Bookings
    path('', BookingListView.as_view(), name='booking-list'),
    path('create/', BookingCreateView.as_view(), name='booking-create'),
    path('upcoming/', upcoming_bookings, name='upcoming-bookings'),
    path('stats/', booking_stats, name='booking-stats'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:pk>/update/', BookingUpdateView.as_view(), name='booking-update'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
    
    # Attachments
    path('<int:booking_id>/attachments/', BookingAttachmentListView.as_view(), name='booking-attachment-list'),
    path('attachments/<int:pk>/', BookingAttachmentDetailView.as_view(), name='booking-attachment-detail'),
]
