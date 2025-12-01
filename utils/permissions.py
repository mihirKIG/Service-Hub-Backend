"""
Custom permission classes
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsCustomer(permissions.BasePermission):
    """
    Permission to only allow customers
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'customer'


class IsProvider(permissions.BasePermission):
    """
    Permission to only allow providers
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'provider'


class IsCustomerOrProvider(permissions.BasePermission):
    """
    Permission for booking-related actions
    Allow customer who created the booking or provider assigned to it
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is the customer who created the booking
        if hasattr(obj, 'customer') and obj.customer == request.user:
            return True
        
        # Check if user is the provider assigned to the booking
        if hasattr(obj, 'provider') and hasattr(request.user, 'provider_profile'):
            return obj.provider == request.user.provider_profile
        
        return False


class IsProviderOwner(permissions.BasePermission):
    """
    Permission to only allow provider to edit their own profile
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the provider profile
        return obj.user == request.user


class IsReviewOwner(permissions.BasePermission):
    """
    Permission to only allow review owner to edit/delete
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user


class IsMessageParticipant(permissions.BasePermission):
    """
    Permission to only allow chat participants to view/send messages
    """
    
    def has_object_permission(self, request, view, obj):
        # For ChatRoom
        if hasattr(obj, 'customer') and hasattr(obj, 'provider'):
            return obj.customer == request.user or obj.provider == request.user
        
        # For Message
        if hasattr(obj, 'chatroom'):
            chatroom = obj.chatroom
            return chatroom.customer == request.user or chatroom.provider == request.user
        
        return False


class IsVerifiedProvider(permissions.BasePermission):
    """
    Permission to only allow verified/approved providers
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'provider_profile'):
            return False
        
        return request.user.provider_profile.status == 'approved'
