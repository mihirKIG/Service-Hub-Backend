from rest_framework import serializers
from .models import Service, ServiceImage, ServiceFAQ
from providers.models import ServiceCategory
from providers.serializers import ProviderSerializer


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories"""
    
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'icon']


class ServiceImageSerializer(serializers.ModelSerializer):
    """Serializer for service images"""
    
    class Meta:
        model = ServiceImage
        fields = ['id', 'image', 'caption', 'order']


class ServiceFAQSerializer(serializers.ModelSerializer):
    """Serializer for service FAQs"""
    
    class Meta:
        model = ServiceFAQ
        fields = ['id', 'question', 'answer', 'order']


class ServiceListSerializer(serializers.ModelSerializer):
    """Serializer for service list view"""
    provider_name = serializers.CharField(source='provider.business_name', read_only=True)
    provider_rating = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'title', 'short_description', 'pricing_type', 'base_price',
            'hourly_rate', 'duration_minutes', 'is_remote', 'is_onsite',
            'status', 'image', 'views_count', 'bookings_count',
            'provider_name', 'provider_rating', 'category_name', 'average_rating',
            'created_at', 'updated_at'
        ]
    
    def get_provider_rating(self, obj):
        """Get provider's average rating"""
        return obj.provider.rating if hasattr(obj.provider, 'rating') else 0


class ServiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for service detail view"""
    provider = ProviderSerializer(read_only=True)
    category = ServiceCategorySerializer(read_only=True)
    images = ServiceImageSerializer(many=True, read_only=True)
    faqs = ServiceFAQSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'provider', 'category', 'title', 'description',
            'short_description', 'pricing_type', 'base_price', 'hourly_rate',
            'duration_minutes', 'is_remote', 'is_onsite', 'status',
            'min_booking_hours', 'max_bookings_per_day', 'image', 'images',
            'faqs', 'views_count', 'bookings_count', 'average_rating',
            'created_at', 'updated_at'
        ]


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating services"""
    images = ServiceImageSerializer(many=True, required=False)
    faqs = ServiceFAQSerializer(many=True, required=False)
    
    class Meta:
        model = Service
        fields = [
            'id', 'category', 'title', 'description', 'short_description',
            'pricing_type', 'base_price', 'hourly_rate', 'duration_minutes',
            'is_remote', 'is_onsite', 'status', 'min_booking_hours',
            'max_bookings_per_day', 'image', 'images', 'faqs'
        ]
    
    def validate(self, data):
        """Validate service data"""
        pricing_type = data.get('pricing_type')
        hourly_rate = data.get('hourly_rate')
        
        if pricing_type == 'hourly' and not hourly_rate:
            raise serializers.ValidationError({
                'hourly_rate': 'Hourly rate is required for hourly pricing type'
            })
        
        return data
    
    def create(self, validated_data):
        """Create service with images and FAQs"""
        images_data = validated_data.pop('images', [])
        faqs_data = validated_data.pop('faqs', [])
        
        # Get provider from request user
        request = self.context.get('request')
        if hasattr(request.user, 'provider_profile'):
            validated_data['provider'] = request.user.provider_profile
        else:
            raise serializers.ValidationError('User must have a provider profile')
        
        service = Service.objects.create(**validated_data)
        
        # Create images
        for image_data in images_data:
            ServiceImage.objects.create(service=service, **image_data)
        
        # Create FAQs
        for faq_data in faqs_data:
            ServiceFAQ.objects.create(service=service, **faq_data)
        
        return service
    
    def update(self, instance, validated_data):
        """Update service with images and FAQs"""
        images_data = validated_data.pop('images', None)
        faqs_data = validated_data.pop('faqs', None)
        
        # Update service fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update images if provided
        if images_data is not None:
            instance.images.all().delete()
            for image_data in images_data:
                ServiceImage.objects.create(service=instance, **image_data)
        
        # Update FAQs if provided
        if faqs_data is not None:
            instance.faqs.all().delete()
            for faq_data in faqs_data:
                ServiceFAQ.objects.create(service=instance, **faq_data)
        
        return instance
