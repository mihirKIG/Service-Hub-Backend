from django.urls import path
from .views import (
    PaymentListView,
    PaymentDetailView,
    PaymentCreateView,
    PaymentMethodListView,
    PaymentMethodDetailView,
    TransactionListView,
    process_refund,
    payment_stats
)

urlpatterns = [
    # Payments
    path('', PaymentListView.as_view(), name='payment-list'),
    path('create/', PaymentCreateView.as_view(), name='payment-create'),
    path('stats/', payment_stats, name='payment-stats'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('<int:pk>/refund/', process_refund, name='payment-refund'),
    
    # Payment Methods
    path('methods/', PaymentMethodListView.as_view(), name='payment-method-list'),
    path('methods/<int:pk>/', PaymentMethodDetailView.as_view(), name='payment-method-detail'),
    
    # Transactions
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
]
