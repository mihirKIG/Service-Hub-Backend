from django.contrib import admin
from .models import Review, ReviewResponse, ReviewImage, ReviewHelpful


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer', 'provider', 'rating', 'title',
        'is_verified', 'is_published', 'helpful_count', 'created_at'
    )
    list_filter = ('rating', 'is_verified', 'is_published', 'is_flagged', 'created_at')
    search_fields = ('title', 'comment', 'customer__email', 'provider__business_name')
    readonly_fields = ('helpful_count', 'created_at', 'updated_at')


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ('review', 'provider', 'created_at')
    search_fields = ('review__title', 'provider__business_name', 'message')


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ('review', 'caption', 'created_at')


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'created_at')
