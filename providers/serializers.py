from rest_framework import serializers
from .models import ServiceCategory, Provider, ProviderAvailability, ProviderPortfolio
from users.serializers import UserSerializer


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for ServiceCategory model"""
    
    class Meta:
        model = ServiceCategory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProviderAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for ProviderAvailability model"""
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = ProviderAvailability
        fields = '__all__'
        read_only_fields = ('provider',)


class ProviderPortfolioSerializer(serializers.ModelSerializer):
    """Serializer for ProviderPortfolio model"""
    
    class Meta:
        model = ProviderPortfolio
        fields = '__all__'
        read_only_fields = ('provider', 'created_at')


class ProviderSerializer(serializers.ModelSerializer):
    """Serializer for Provider model"""
    user = UserSerializer(read_only=True)
    categories = ServiceCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=ServiceCategory.objects.all(),
        source='categories'
    )
    availability = ProviderAvailabilitySerializer(many=True, read_only=True)
    portfolio = ProviderPortfolioSerializer(many=True, read_only=True)
    completion_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Provider
        fields = '__all__'
        read_only_fields = (
            'user', 'average_rating', 'total_reviews',
            'total_bookings', 'completed_bookings', 'created_at', 'updated_at'
        )


class ProviderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for provider listings"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    categories = ServiceCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Provider
        fields = (
            'id', 'user_name', 'business_name', 'bio', 'categories',
            'hourly_rate', 'city', 'state', 'average_rating',
            'total_reviews', 'completion_rate', 'is_available'
        )


class ProviderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating provider profile"""
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ServiceCategory.objects.all(),
        source='categories'
    )
    
    class Meta:
        model = Provider
        fields = (
            'business_name', 'bio', 'category_ids', 'experience_years',
            'hourly_rate', 'city', 'state', 'country', 'postal_code',
            'latitude', 'longitude', 'id_document', 'certifications'
        )
    
    def create(self, validated_data):
        categories = validated_data.pop('categories')
        user = self.context['request'].user
        provider = Provider.objects.create(user=user, **validated_data)
        provider.categories.set(categories)
        return provider
