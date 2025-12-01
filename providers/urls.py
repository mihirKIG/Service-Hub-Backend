from django.urls import path
from .views import (
    ServiceCategoryListView,
    ServiceCategoryDetailView,
    ProviderListView,
    ProviderDetailView,
    ProviderCreateView,
    ProviderUpdateView,
    MyProviderProfileView,
    ProviderAvailabilityListView,
    ProviderAvailabilityDetailView,
    ProviderPortfolioListView,
    ProviderPortfolioDetailView,
    approve_provider,
    reject_provider
)

urlpatterns = [
    # Service Categories
    path('categories/', ServiceCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', ServiceCategoryDetailView.as_view(), name='category-detail'),
    
    # Providers
    path('', ProviderListView.as_view(), name='provider-list'),
    path('create/', ProviderCreateView.as_view(), name='provider-create'),
    path('me/', MyProviderProfileView.as_view(), name='my-provider-profile'),
    path('me/update/', ProviderUpdateView.as_view(), name='provider-update'),
    path('<int:pk>/', ProviderDetailView.as_view(), name='provider-detail'),
    
    # Provider Actions (Admin)
    path('<int:pk>/approve/', approve_provider, name='provider-approve'),
    path('<int:pk>/reject/', reject_provider, name='provider-reject'),
    
    # Availability
    path('availability/', ProviderAvailabilityListView.as_view(), name='availability-list'),
    path('availability/<int:pk>/', ProviderAvailabilityDetailView.as_view(), name='availability-detail'),
    
    # Portfolio
    path('portfolio/', ProviderPortfolioListView.as_view(), name='portfolio-list'),
    path('portfolio/<int:pk>/', ProviderPortfolioDetailView.as_view(), name='portfolio-detail'),
]
