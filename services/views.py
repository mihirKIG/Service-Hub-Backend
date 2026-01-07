from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from .models import Service, ServiceImage, ServiceFAQ
from .serializers import (
    ServiceListSerializer, ServiceDetailSerializer,
    ServiceCreateUpdateSerializer, ServiceImageSerializer,
    ServiceFAQSerializer
)
from utils.permissions import IsProviderOwner


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing services
    
    List: Get all active services (public)
    Retrieve: Get service details (public)
    Create: Create new service (provider only)
    Update: Update service (owner only)
    Delete: Delete service (owner only)
    """
    queryset = Service.objects.select_related('provider', 'category').prefetch_related('images', 'faqs')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'pricing_type', 'status', 'is_remote', 'is_onsite']
    search_fields = ['title', 'description', 'short_description', 'provider__business_name']
    ordering_fields = ['created_at', 'base_price', 'views_count', 'bookings_count', 'title']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve', 'search', 'featured', 'popular']:
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), IsProviderOwner()]
        
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return ServiceListSerializer
        elif self.action == 'retrieve':
            return ServiceDetailSerializer
        else:
            return ServiceCreateUpdateSerializer
    
    def get_queryset(self):
        """Filter queryset based on action and user"""
        queryset = super().get_queryset()
        
        # For list/retrieve, show only active services to non-owners
        if self.action in ['list', 'retrieve']:
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(status='active')
            elif hasattr(self.request.user, 'provider_profile'):
                # Providers can see their own services regardless of status
                queryset = queryset.filter(
                    Q(status='active') | Q(provider=self.request.user.provider_profile)
                )
            else:
                queryset = queryset.filter(status='active')
        
        # Custom filters
        provider_id = self.request.query_params.get('provider', None)
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve service and increment view count"""
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured services (high ratings and bookings)"""
        queryset = self.get_queryset().filter(status='active')
        queryset = queryset.annotate(
            booking_count=Count('provider__bookings')
        ).order_by('-booking_count', '-views_count')[:10]
        
        serializer = ServiceListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular services by views"""
        queryset = self.get_queryset().filter(status='active').order_by('-views_count')[:10]
        serializer = ServiceListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_services(self, request):
        """Get services for authenticated provider"""
        if not hasattr(request.user, 'provider_profile'):
            return Response(
                {'error': 'You must be a provider to access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(provider=request.user.provider_profile)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ServiceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ServiceListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        """Add an image to service"""
        service = self.get_object()
        serializer = ServiceImageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(service=service)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_faq(self, request, pk=None):
        """Add FAQ to service"""
        service = self.get_object()
        serializer = ServiceFAQSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(service=service)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_image(self, request, pk=None):
        """Remove an image from service"""
        service = self.get_object()
        image_id = request.data.get('image_id')
        
        try:
            image = ServiceImage.objects.get(id=image_id, service=service)
            image.delete()
            return Response({'message': 'Image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ServiceImage.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def remove_faq(self, request, pk=None):
        """Remove FAQ from service"""
        service = self.get_object()
        faq_id = request.data.get('faq_id')
        
        try:
            faq = ServiceFAQ.objects.get(id=faq_id, service=service)
            faq.delete()
            return Response({'message': 'FAQ deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ServiceFAQ.DoesNotExist:
            return Response({'error': 'FAQ not found'}, status=status.HTTP_404_NOT_FOUND)
