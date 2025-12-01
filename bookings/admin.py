from django.contrib import admin
from .models import Booking, BookingAttachment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'service_title', 'customer', 'provider', 'booking_date',
        'start_time', 'status', 'total_amount', 'created_at'
    )
    list_filter = ('status', 'booking_date', 'created_at')
    search_fields = ('service_title', 'customer__email', 'provider__business_name', 'city')
    readonly_fields = ('total_amount', 'created_at', 'updated_at', 'confirmed_at', 'completed_at', 'cancelled_at')
    date_hierarchy = 'booking_date'


@admin.register(BookingAttachment)
class BookingAttachmentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'uploaded_by', 'description', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('booking__service_title', 'uploaded_by__email', 'description')
