from django.contrib import admin
from django.contrib import messages
from .models import Service, ServiceImage, ServiceFAQ


class ServiceImageInline(admin.TabularInline):
    """Inline admin for service images"""
    model = ServiceImage
    extra = 1
    fields = ('image', 'caption', 'order')


class ServiceFAQInline(admin.TabularInline):
    """Inline admin for service FAQs"""
    model = ServiceFAQ
    extra = 1
    fields = ('question', 'answer', 'order')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin interface for Service model"""
    list_display = ('title', 'provider', 'category', 'pricing_type', 'base_price', 'status', 'views_count', 'bookings_count', 'created_at')
    list_filter = ('status', 'pricing_type', 'category', 'is_remote', 'is_onsite', 'created_at')
    search_fields = ('title', 'description', 'provider__business_name')
    readonly_fields = ('views_count', 'bookings_count', 'created_at', 'updated_at')
    filter_horizontal = ()
    inlines = [ServiceImageInline, ServiceFAQInline]
    autocomplete_fields = ['provider', 'category']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('provider', 'category', 'title', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('pricing_type', 'base_price', 'hourly_rate')
        }),
        ('Service Details', {
            'fields': ('duration_minutes', 'is_remote', 'is_onsite', 'image')
        }),
        ('Availability', {
            'fields': ('status', 'min_booking_hours', 'max_bookings_per_day')
        }),
        ('Statistics', {
            'fields': ('views_count', 'bookings_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize the form to provide helpful messages"""
        form = super().get_form(request, obj, **kwargs)
        
        # Check if there are any categories
        from providers.models import ServiceCategory
        if not ServiceCategory.objects.exists():
            messages.warning(request, 'Please create at least one Service Category first!')
        
        # Check if there are any providers
        from providers.models import Provider
        if not Provider.objects.exists():
            messages.warning(request, 'Please create at least one Provider first!')
        
        return form
    
    def save_model(self, request, obj, form, change):
        """Auto-save with helpful messages"""
        super().save_model(request, obj, form, change)
        if not change:  # Only for new objects
            messages.success(request, f'Service "{obj.title}" created successfully!')


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    """Admin interface for ServiceImage model"""
    list_display = ('service', 'caption', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('service__title', 'caption')


@admin.register(ServiceFAQ)
class ServiceFAQAdmin(admin.ModelAdmin):
    """Admin interface for ServiceFAQ model"""
    list_display = ('service', 'question', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('service__title', 'question', 'answer')
