from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import ServiceCategory, Provider, ProviderAvailability, ProviderPortfolio
from .serializers import (
    ServiceCategorySerializer,
    ProviderSerializer,
    ProviderListSerializer,
    ProviderCreateSerializer,
    ProviderAvailabilitySerializer,
    ProviderPortfolioSerializer
)


# Service Category Views
class ServiceCategoryListView(generics.ListCreateAPIView):
    """List all service categories or create a new one"""
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ServiceCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service category"""
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.IsAdminUser]


# Provider Views
class ProviderListView(generics.ListAPIView):
    """List all approved providers with search and filters"""
    queryset = Provider.objects.filter(status='approved')
    serializer_class = ProviderListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['business_name', 'bio', 'city', 'state']
    ordering_fields = ['average_rating', 'hourly_rate', 'created_at']
    ordering = ['-average_rating']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(categories__id=category)
        
        # Filter by location
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by availability
        is_available = self.request.query_params.get('is_available', None)
        if is_available:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.filter(average_rating__gte=float(min_rating))
        
        return queryset.distinct()


class ProviderDetailView(generics.RetrieveAPIView):
    """Retrieve provider details"""
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.AllowAny]


class ProviderCreateView(generics.CreateAPIView):
    """Create a provider profile"""
    serializer_class = ProviderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Check if user already has a provider profile
        if hasattr(request.user, 'provider_profile'):
            return Response(
                {'error': 'Provider profile already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.save()
        
        return Response(
            ProviderSerializer(provider).data,
            status=status.HTTP_201_CREATED
        )


class ProviderUpdateView(generics.UpdateAPIView):
    """Update provider profile"""
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.provider_profile


class MyProviderProfileView(generics.RetrieveAPIView):
    """Get current user's provider profile"""
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.provider_profile


# Provider Availability Views
class ProviderAvailabilityListView(generics.ListCreateAPIView):
    """List and create provider availability"""
    serializer_class = ProviderAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProviderAvailability.objects.filter(provider=self.request.user.provider_profile)
    
    def perform_create(self, serializer):
        serializer.save(provider=self.request.user.provider_profile)


class ProviderAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete provider availability"""
    serializer_class = ProviderAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProviderAvailability.objects.filter(provider=self.request.user.provider_profile)


# Provider Portfolio Views
class ProviderPortfolioListView(generics.ListCreateAPIView):
    """List and create provider portfolio items"""
    serializer_class = ProviderPortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProviderPortfolio.objects.filter(provider=self.request.user.provider_profile)
    
    def perform_create(self, serializer):
        serializer.save(provider=self.request.user.provider_profile)


class ProviderPortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete portfolio item"""
    serializer_class = ProviderPortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProviderPortfolio.objects.filter(provider=self.request.user.provider_profile)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def approve_provider(request, pk):
    """Approve a provider (Admin only)"""
    try:
        provider = Provider.objects.get(pk=pk)
        provider.status = 'approved'
        provider.save()
        return Response({'message': 'Provider approved successfully'}, status=status.HTTP_200_OK)
    except Provider.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def reject_provider(request, pk):
    """Reject a provider (Admin only)"""
    try:
        provider = Provider.objects.get(pk=pk)
        provider.status = 'rejected'
        provider.save()
        return Response({'message': 'Provider rejected'}, status=status.HTTP_200_OK)
    except Provider.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)
