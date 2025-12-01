from django.urls import path
from .views import (
    ReviewListView,
    ReviewDetailView,
    ReviewCreateView,
    ReviewUpdateView,
    ReviewDeleteView,
    MyReviewsView,
    ProviderReviewsView,
    ReviewResponseCreateView,
    ReviewImageCreateView,
    mark_review_helpful,
    provider_review_stats
)

urlpatterns = [
    # Reviews
    path('', ReviewListView.as_view(), name='review-list'),
    path('create/', ReviewCreateView.as_view(), name='review-create'),
    path('my-reviews/', MyReviewsView.as_view(), name='my-reviews'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('<int:pk>/update/', ReviewUpdateView.as_view(), name='review-update'),
    path('<int:pk>/delete/', ReviewDeleteView.as_view(), name='review-delete'),
    path('<int:pk>/helpful/', mark_review_helpful, name='review-helpful'),
    
    # Provider Reviews
    path('provider/<int:provider_id>/', ProviderReviewsView.as_view(), name='provider-reviews'),
    path('provider/<int:provider_id>/stats/', provider_review_stats, name='provider-review-stats'),
    
    # Review Responses
    path('<int:review_id>/response/', ReviewResponseCreateView.as_view(), name='review-response-create'),
    
    # Review Images
    path('<int:review_id>/images/', ReviewImageCreateView.as_view(), name='review-image-create'),
]
