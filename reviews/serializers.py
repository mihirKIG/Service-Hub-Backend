from rest_framework import serializers
from .models import Review, ReviewResponse, ReviewImage, ReviewHelpful
from users.serializers import UserSerializer


class ReviewImageSerializer(serializers.ModelSerializer):
    """Serializer for ReviewImage model"""
    
    class Meta:
        model = ReviewImage
        fields = '__all__'
        read_only_fields = ('review', 'created_at')


class ReviewResponseSerializer(serializers.ModelSerializer):
    """Serializer for ReviewResponse model"""
    provider_name = serializers.CharField(source='provider.business_name', read_only=True)
    
    class Meta:
        model = ReviewResponse
        fields = '__all__'
        read_only_fields = ('provider', 'created_at', 'updated_at')


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    customer = UserSerializer(read_only=True)
    provider_name = serializers.CharField(source='provider.business_name', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    response = ReviewResponseSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = (
            'customer', 'provider', 'booking', 'is_verified',
            'helpful_count', 'created_at', 'updated_at'
        )


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    booking_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = (
            'booking_id', 'rating', 'title', 'comment',
            'quality_rating', 'professionalism_rating',
            'punctuality_rating', 'value_rating'
        )
    
    def validate_booking_id(self, value):
        from bookings.models import Booking
        try:
            booking = Booking.objects.get(id=value)
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Booking not found")
        
        # Check if booking is completed
        if booking.status != 'completed':
            raise serializers.ValidationError("Only completed bookings can be reviewed")
        
        # Check if review already exists
        if hasattr(booking, 'review'):
            raise serializers.ValidationError("Review already exists for this booking")
        
        # Check if user is the customer
        if booking.customer != self.context['request'].user:
            raise serializers.ValidationError("You can only review your own bookings")
        
        return value
    
    def create(self, validated_data):
        booking_id = validated_data.pop('booking_id')
        booking = Booking.objects.get(id=booking_id)
        
        review = Review.objects.create(
            booking=booking,
            provider=booking.provider,
            customer=self.context['request'].user,
            **validated_data
        )
        return review


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reviews"""
    
    class Meta:
        model = Review
        fields = (
            'rating', 'title', 'comment',
            'quality_rating', 'professionalism_rating',
            'punctuality_rating', 'value_rating'
        )
