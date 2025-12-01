from django.contrib import admin
from .models import Payment, PaymentMethod, Transaction


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer', 'amount', 'currency', 'payment_method',
        'status', 'transaction_id', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'customer__email', 'booking__service_title')
    readonly_fields = ('transaction_id', 'gateway_response', 'created_at', 'updated_at', 'completed_at', 'refunded_at')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_type', 'last_four', 'expiry_month', 'expiry_year', 'is_default', 'is_active')
    list_filter = ('card_type', 'is_default', 'is_active')
    search_fields = ('user__email', 'last_four')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'transaction_type', 'amount', 'currency', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__email', 'reference_id', 'description')
