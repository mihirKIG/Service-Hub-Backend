from rest_framework import serializers
from .models import Payment, PaymentMethod, Transaction
from bookings.serializers import BookingSerializer


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    booking = BookingSerializer(read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = (
            'customer', 'transaction_id', 'gateway_response',
            'refund_amount', 'refunded_at', 'created_at',
            'updated_at', 'completed_at'
        )


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating a payment"""
    booking_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    payment_method_id = serializers.CharField(required=False)  # For saved payment methods
    
    def validate_booking_id(self, value):
        from bookings.models import Booking
        try:
            booking = Booking.objects.get(id=value)
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Booking not found")
        
        # Check if booking already has a payment
        if hasattr(booking, 'payment'):
            raise serializers.ValidationError("Payment already exists for this booking")
        
        # Check if booking is in correct status
        if booking.status not in ['pending', 'confirmed']:
            raise serializers.ValidationError("Cannot create payment for this booking status")
        
        return value


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model"""
    
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class PaymentMethodCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment method"""
    
    class Meta:
        model = PaymentMethod
        fields = (
            'card_type', 'last_four', 'expiry_month', 'expiry_year',
            'stripe_payment_method_id', 'is_default'
        )


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class RefundSerializer(serializers.Serializer):
    """Serializer for processing refunds"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason = serializers.CharField(required=True)
    
    def validate_amount(self, value):
        payment = self.context.get('payment')
        if value and value > payment.amount:
            raise serializers.ValidationError("Refund amount cannot exceed payment amount")
        return value
