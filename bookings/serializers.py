from rest_framework import serializers
from .models import Booking, BookingAttachment
from providers.serializers import ProviderListSerializer
from users.serializers import UserSerializer


class BookingAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for BookingAttachment model"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = BookingAttachment
        fields = '__all__'
        read_only_fields = ('booking', 'uploaded_by', 'created_at')


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    customer = UserSerializer(read_only=True)
    provider = ProviderListSerializer(read_only=True)
    attachments = BookingAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = (
            'customer', 'total_amount', 'created_at', 'updated_at',
            'confirmed_at', 'completed_at', 'cancelled_at'
        )


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings"""
    provider_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Booking
        fields = (
            'provider_id', 'service_title', 'service_description',
            'booking_date', 'start_time', 'end_time', 'duration_hours',
            'service_address', 'city', 'postal_code', 'customer_notes'
        )
    
    def validate(self, attrs):
        from providers.models import Provider
        from django.utils import timezone
        import datetime
        
        # Validate provider exists
        try:
            provider = Provider.objects.get(id=attrs['provider_id'])
        except Provider.DoesNotExist:
            raise serializers.ValidationError({"provider_id": "Provider not found"})
        
        # Validate provider is available
        if not provider.is_available or provider.status != 'approved':
            raise serializers.ValidationError({"provider_id": "Provider is not available"})
        
        # Validate booking date is in the future
        booking_datetime = datetime.datetime.combine(attrs['booking_date'], attrs['start_time'])
        if timezone.make_aware(booking_datetime) < timezone.now():
            raise serializers.ValidationError({"booking_date": "Booking date must be in the future"})
        
        # Validate end time is after start time
        if attrs['end_time'] <= attrs['start_time']:
            raise serializers.ValidationError({"end_time": "End time must be after start time"})
        
        attrs['provider'] = provider
        attrs['hourly_rate'] = provider.hourly_rate
        
        return attrs
    
    def create(self, validated_data):
        provider_id = validated_data.pop('provider_id')
        provider = validated_data.pop('provider')
        customer = self.context['request'].user
        
        booking = Booking.objects.create(
            customer=customer,
            provider=provider,
            **validated_data
        )
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking status"""
    
    class Meta:
        model = Booking
        fields = ('status', 'provider_notes', 'cancellation_reason')
    
    def validate_status(self, value):
        current_status = self.instance.status
        
        # Define valid status transitions
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': ['refunded'],
            'refunded': []
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}"
            )
        
        return value
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        
        status = validated_data.get('status')
        
        # Update timestamp based on status
        if status == 'confirmed' and not instance.confirmed_at:
            instance.confirmed_at = timezone.now()
        elif status == 'completed' and not instance.completed_at:
            instance.completed_at = timezone.now()
            # Update provider stats
            instance.provider.completed_bookings += 1
            instance.provider.save()
        elif status == 'cancelled' and not instance.cancelled_at:
            instance.cancelled_at = timezone.now()
            instance.cancelled_by = self.context['request'].user
        
        return super().update(instance, validated_data)
