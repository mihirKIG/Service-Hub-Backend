from django.contrib import admin
from .models import ServiceCategory, Provider, ProviderAvailability, ProviderPortfolio


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'status', 'city', 'hourly_rate', 'average_rating', 'is_available')
    list_filter = ('status', 'is_available', 'city', 'state')
    search_fields = ('business_name', 'user__phone', 'user__email', 'city')
    filter_horizontal = ('categories',)
    readonly_fields = ('average_rating', 'total_reviews', 'total_bookings', 'completed_bookings')


@admin.register(ProviderAvailability)
class ProviderAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('provider', 'day_of_week', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available')


@admin.register(ProviderPortfolio)
class ProviderPortfolioAdmin(admin.ModelAdmin):
    list_display = ('provider', 'title', 'created_at')
    search_fields = ('provider__business_name', 'title')
