from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import Review, ReviewResponse, ReviewImage, ReviewHelpful
from .serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    ReviewResponseSerializer,
    ReviewImageSerializer
)


class ReviewListView(generics.ListAPIView):
    """List all reviews with filters"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'comment']
    ordering_fields = ['rating', 'created_at', 'helpful_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_published=True)
        
        # Filter by provider
        provider_id = self.request.query_params.get('provider_id', None)
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.filter(rating__gte=int(min_rating))
        
        # Filter by verified reviews only
        verified_only = self.request.query_params.get('verified_only', None)
        if verified_only == 'true':
            queryset = queryset.filter(is_verified=True)
        
        return queryset


class ReviewDetailView(generics.RetrieveAPIView):
    """Retrieve review details"""
    queryset = Review.objects.filter(is_published=True)
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]


class ReviewCreateView(generics.CreateAPIView):
    """Create a new review"""
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_201_CREATED
        )


class ReviewUpdateView(generics.UpdateAPIView):
    """Update a review"""
    serializer_class = ReviewUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(customer=self.request.user)


class ReviewDeleteView(generics.DestroyAPIView):
    """Delete a review"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(customer=self.request.user)


class MyReviewsView(generics.ListAPIView):
    """List reviews created by authenticated user"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(customer=self.request.user)


class ProviderReviewsView(generics.ListAPIView):
    """List reviews for a specific provider"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        provider_id = self.kwargs.get('provider_id')
        return Review.objects.filter(provider_id=provider_id, is_published=True)


# Review Response
class ReviewResponseCreateView(generics.CreateAPIView):
    """Create a response to a review (Provider only)"""
    serializer_class = ReviewResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        review_id = kwargs.get('review_id')
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response(
                {'error': 'Review not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is the provider
        if not hasattr(request.user, 'provider_profile'):
            return Response(
                {'error': 'Only providers can respond to reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if review.provider != request.user.provider_profile:
            return Response(
                {'error': 'You can only respond to reviews for your services'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if response already exists
        if hasattr(review, 'response'):
            return Response(
                {'error': 'Response already exists for this review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response = ReviewResponse.objects.create(
            review=review,
            provider=request.user.provider_profile,
            message=request.data.get('message')
        )
        
        return Response(
            ReviewResponseSerializer(response).data,
            status=status.HTTP_201_CREATED
        )


# Review Images
class ReviewImageCreateView(generics.CreateAPIView):
    """Add images to a review"""
    serializer_class = ReviewImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = Review.objects.get(id=review_id, customer=self.request.user)
        serializer.save(review=review)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_review_helpful(request, pk):
    """Mark a review as helpful"""
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response(
            {'error': 'Review not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user already marked this review as helpful
    helpful, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user
    )
    
    if created:
        review.helpful_count += 1
        review.save()
        return Response({'message': 'Review marked as helpful'}, status=status.HTTP_200_OK)
    else:
        # Remove the helpful mark
        helpful.delete()
        review.helpful_count = max(0, review.helpful_count - 1)
        review.save()
        return Response({'message': 'Helpful mark removed'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def provider_review_stats(request, provider_id):
    """Get review statistics for a provider"""
    from providers.models import Provider
    
    try:
        provider = Provider.objects.get(id=provider_id)
    except Provider.DoesNotExist:
        return Response(
            {'error': 'Provider not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    reviews = Review.objects.filter(provider=provider, is_published=True)
    
    # Rating distribution
    rating_distribution = {
        '5_star': reviews.filter(rating=5).count(),
        '4_star': reviews.filter(rating=4).count(),
        '3_star': reviews.filter(rating=3).count(),
        '2_star': reviews.filter(rating=2).count(),
        '1_star': reviews.filter(rating=1).count(),
    }
    
    # Average sub-ratings
    sub_ratings = reviews.aggregate(
        avg_quality=Avg('quality_rating'),
        avg_professionalism=Avg('professionalism_rating'),
        avg_punctuality=Avg('punctuality_rating'),
        avg_value=Avg('value_rating')
    )
    
    stats = {
        'total_reviews': provider.total_reviews,
        'average_rating': float(provider.average_rating),
        'rating_distribution': rating_distribution,
        'sub_ratings': {
            'quality': round(sub_ratings['avg_quality'] or 0, 2),
            'professionalism': round(sub_ratings['avg_professionalism'] or 0, 2),
            'punctuality': round(sub_ratings['avg_punctuality'] or 0, 2),
            'value': round(sub_ratings['avg_value'] or 0, 2),
        }
    }
    
    return Response(stats)
