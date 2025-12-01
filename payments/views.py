from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Payment, PaymentMethod, Transaction
from .serializers import (
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentMethodSerializer,
    PaymentMethodCreateSerializer,
    TransactionSerializer,
    RefundSerializer
)
from bookings.models import Booking


class PaymentListView(generics.ListAPIView):
    """List all payments for authenticated user"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(customer=user)


class PaymentDetailView(generics.RetrieveAPIView):
    """Retrieve payment details"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(customer=self.request.user)


class PaymentCreateView(generics.CreateAPIView):
    """Create a payment for a booking"""
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        booking = Booking.objects.get(id=serializer.validated_data['booking_id'])
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            customer=request.user,
            amount=booking.total_amount,
            payment_method=serializer.validated_data['payment_method'],
            status='processing'
        )
        
        # TODO: Integrate with actual payment gateway (Stripe, PayPal, etc.)
        # For now, simulate successful payment
        try:
            # Simulate payment processing
            payment.status = 'completed'
            payment.transaction_id = f"TXN-{payment.id}-{timezone.now().timestamp()}"
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update booking status
            booking.status = 'confirmed'
            booking.confirmed_at = timezone.now()
            booking.save()
            
            # Create transaction record
            Transaction.objects.create(
                payment=payment,
                user=request.user,
                transaction_type='payment',
                amount=payment.amount,
                description=f"Payment for booking: {booking.service_title}"
            )
            
            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            payment.status = 'failed'
            payment.gateway_response = {'error': str(e)}
            payment.save()
            
            return Response(
                {'error': 'Payment processing failed'},
                status=status.HTTP_400_BAD_REQUEST
            )


# Payment Methods
class PaymentMethodListView(generics.ListCreateAPIView):
    """List and create payment methods"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentMethodCreateSerializer
        return PaymentMethodSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete payment method"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()


# Transactions
class TransactionListView(generics.ListAPIView):
    """List all transactions for authenticated user"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(user=user)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_refund(request, pk):
    """Process a refund for a payment"""
    try:
        payment = Payment.objects.get(pk=pk, customer=request.user)
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if payment can be refunded
    if payment.status != 'completed':
        return Response(
            {'error': 'Only completed payments can be refunded'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if payment.status == 'refunded':
        return Response(
            {'error': 'Payment already refunded'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = RefundSerializer(data=request.data, context={'payment': payment})
    serializer.is_valid(raise_exception=True)
    
    refund_amount = serializer.validated_data.get('amount', payment.amount)
    
    # TODO: Process refund with payment gateway
    # For now, simulate successful refund
    payment.status = 'refunded'
    payment.refund_amount = refund_amount
    payment.refund_reason = serializer.validated_data['reason']
    payment.refunded_at = timezone.now()
    payment.save()
    
    # Update booking status
    payment.booking.status = 'refunded'
    payment.booking.save()
    
    # Create transaction record
    Transaction.objects.create(
        payment=payment,
        user=request.user,
        transaction_type='refund',
        amount=refund_amount,
        description=f"Refund for booking: {payment.booking.service_title}"
    )
    
    return Response(
        PaymentSerializer(payment).data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_stats(request):
    """Get payment statistics for authenticated user"""
    user = request.user
    
    payments = Payment.objects.filter(customer=user)
    
    stats = {
        'total_payments': payments.count(),
        'completed_payments': payments.filter(status='completed').count(),
        'pending_payments': payments.filter(status='pending').count(),
        'failed_payments': payments.filter(status='failed').count(),
        'total_amount_paid': sum(p.amount for p in payments.filter(status='completed')),
        'total_refunded': sum(p.refund_amount for p in payments.filter(status='refunded')),
    }
    
    return Response(stats)
