from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    GoogleAuthSerializer,
    UserProfileUpdateSerializer
)

User = get_user_model()


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# class SendOTPView(APIView):
#     """
#     POST /api/auth/send-otp/
#     Send 6-digit OTP to phone number (stored in Redis/Cache for 2 minutes)
#     """
#     permission_classes = [permissions.AllowAny]
    
#     def post(self, request):
#         serializer = SendOTPSerializer(data=request.data)
        
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         result = serializer.save()
        
#         # TODO: In production, send OTP via SMS (Twilio, AWS SNS, etc.)
#         # For development/testing, we return the OTP
        
#         return Response({
#             'success': True,
#             'message': 'OTP sent successfully',
#             'phone': result['phone'],
#             'otp': result['otp'],  # REMOVE THIS IN PRODUCTION
#             'expires_in_seconds': result['expires_in_seconds']
#         }, status=status.HTTP_200_OK)


class SendOTPView(APIView):
    """
    POST /api/users/send-otp/
    Send 6-digit OTP to phone number via BulkSMSBD
    OTP stored in cache for 120 seconds
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """
    POST /api/auth/verify-otp/
    Verify OTP and login user (auto-register if new phone)
    Returns JWT access & refresh tokens
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        first_name = serializer.validated_data.get('first_name', '')
        last_name = serializer.validated_data.get('last_name', '')
        email = serializer.validated_data.get('email', None)
        
        # Check if user exists
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'is_verified': True,
            }
        )
        
        # Update verification status if user already exists
        if not created and not user.is_verified:
            user.is_verified = True
            user.save(update_fields=['is_verified'])
        
        # Generate JWT tokens
        tokens = get_tokens_for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful' if not created else 'Registration successful',
            'created': created,
            'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_200_OK)


class GoogleAuthView(APIView):
    """
    POST /api/users/google/
    Firebase Google Sign-In authentication
    Creates user if new, returns JWT tokens
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            serializer = GoogleAuthSerializer(data=request.data, context={'request': request})
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get verified Google user info from serializer context
            google_info = serializer.context['google_user_info']
            google_uid = google_info['google_uid']
            
            # Check if user exists by google_uid
            try:
                user = User.objects.get(google_uid=google_uid)
                created = False
                
                # Update profile if data changed
                updated = False
                if google_info.get('email') and user.email != google_info['email']:
                    user.email = google_info['email']
                    updated = True
                if google_info.get('profile_picture') and user.profile_picture != google_info['profile_picture']:
                    user.profile_picture = google_info['profile_picture']
                    updated = True
                if updated:
                    user.save()
                
            except User.DoesNotExist:
                # Create new user with Google account
                # Use Firebase UID as phone placeholder
                phone = f"+google_{google_uid[:10]}"
                
                user = User.objects.create(
                    # phone=phone,
                    google_uid=google_uid,
                    email=google_info.get('email'),
                    first_name=google_info.get('first_name', ''),
                    last_name=google_info.get('last_name', ''),
                    profile_picture=google_info.get('profile_picture'),
                    is_verified=True,  # Firebase accounts are pre-verified
                )
                created = True
            
            # Generate JWT tokens
            tokens = get_tokens_for_user(user)
            
            return Response({
                'success': True,
                'message': 'Login successful' if not created else 'Registration successful',
                'created': created,
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Google Auth Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'error': str(e),
                'detail': 'An error occurred during Google authentication'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/auth/profile/
    PATCH /api/auth/profile/
    View and update authenticated user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = UserProfileUpdateSerializer(
            self.get_object(),
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': UserSerializer(self.get_object()).data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Logout user by blacklisting refresh token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'success': False,
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
