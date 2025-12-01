from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import Booking, BookingAttachment
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
    BookingAttachmentSerializer
)
from utils.permissions import IsCustomerOrProvider


class BookingListView(generics.ListAPIView):
    """List all bookings for the authenticated user"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['service_title', 'service_description', 'city']
    ordering_fields = ['booking_date', 'created_at', 'total_amount']
    ordering = ['-booking_date']
    
    def get_queryset(self):
        user = self.request.user
        
        # If user is a provider, show bookings for their provider profile
        if hasattr(user, 'provider_profile'):
            queryset = Booking.objects.filter(provider=user.provider_profile)
        else:
            # Otherwise show bookings where user is the customer
            queryset = Booking.objects.filter(customer=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(booking_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(booking_date__lte=end_date)
        
        return queryset


class BookingDetailView(generics.RetrieveAPIView):
    """Retrieve booking details"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrProvider]
    
    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(customer=user) | Q(provider__user=user)
        )


class BookingCreateView(generics.CreateAPIView):
    """Create a new booking"""
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        
        # Update provider booking count
        booking.provider.total_bookings += 1
        booking.provider.save()
        
        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )


class BookingUpdateView(generics.UpdateAPIView):
    """Update booking status"""
    serializer_class = BookingUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrProvider]
    
    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(customer=user) | Q(provider__user=user)
        )


class BookingCancelView(generics.UpdateAPIView):
    """Cancel a booking"""
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrProvider]
    
    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(customer=user) | Q(provider__user=user)
        )
    
    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        
        # Check if booking can be cancelled
        if booking.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Only pending or confirmed bookings can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancelled_by = request.user
        booking.cancellation_reason = request.data.get('cancellation_reason', '')
        booking.save()
        
        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_200_OK
        )


# Booking Attachments
class BookingAttachmentListView(generics.ListCreateAPIView):
    """List and create booking attachments"""
    serializer_class = BookingAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        booking_id = self.kwargs.get('booking_id')
        return BookingAttachment.objects.filter(booking_id=booking_id)
    
    def perform_create(self, serializer):
        booking_id = self.kwargs.get('booking_id')
        booking = Booking.objects.get(id=booking_id)
        
        # Verify user has access to this booking
        user = self.request.user
        if booking.customer != user and booking.provider.user != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to add attachments to this booking")
        
        serializer.save(booking=booking, uploaded_by=user)


class BookingAttachmentDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete booking attachment"""
    serializer_class = BookingAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BookingAttachment.objects.all()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def upcoming_bookings(request):
    """Get upcoming bookings for the user"""
    user = request.user
    
    if hasattr(user, 'provider_profile'):
        bookings = Booking.objects.filter(
            provider=user.provider_profile,
            booking_date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).order_by('booking_date', 'start_time')[:5]
    else:
        bookings = Booking.objects.filter(
            customer=user,
            booking_date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).order_by('booking_date', 'start_time')[:5]
    
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def booking_stats(request):
    """Get booking statistics for the user"""
    user = request.user
    
    if hasattr(user, 'provider_profile'):
        provider = user.provider_profile
        stats = {
            'total_bookings': provider.total_bookings,
            'completed_bookings': provider.completed_bookings,
            'completion_rate': provider.completion_rate,
            'pending_bookings': Booking.objects.filter(provider=provider, status='pending').count(),
            'confirmed_bookings': Booking.objects.filter(provider=provider, status='confirmed').count(),
        }
    else:
        stats = {
            'total_bookings': Booking.objects.filter(customer=user).count(),
            'completed_bookings': Booking.objects.filter(customer=user, status='completed').count(),
            'pending_bookings': Booking.objects.filter(customer=user, status='pending').count(),
            'cancelled_bookings': Booking.objects.filter(customer=user, status='cancelled').count(),
        }
    
    return Response(stats)
