from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import OTP
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    ChangePasswordSerializer,
    UserProfileUpdateSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    GoogleLoginSerializer
)

User = get_user_model()


class SendOTPView(APIView):
    """Send OTP to phone number"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            
            # Generate OTP
            otp_code = OTP.generate_otp()
            
            # Save OTP to database
            otp_obj = OTP.objects.create(
                phone=phone,
                otp=otp_code
            )
            
            # TODO: Send OTP via SMS service (Twilio, AWS SNS, etc.)
            # For development, return OTP in response (REMOVE IN PRODUCTION)
            
            return Response({
                'message': 'OTP sent successfully',
                'phone': phone,
                'otp': otp_code,  # REMOVE THIS IN PRODUCTION
                'expires_in': '5 minutes'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """Verify OTP and login/register user"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            otp_obj = serializer.validated_data['otp_obj']
            
            # Mark OTP as verified
            otp_obj.is_verified = True
            otp_obj.save()
            
            # Check if user exists
            try:
                user = User.objects.get(phone=phone)
                created = False
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create_user(
                    phone=phone,
                    first_name=serializer.validated_data.get('first_name', ''),
                    last_name=serializer.validated_data.get('last_name', ''),
                    email=serializer.validated_data.get('email', ''),
                    user_type=serializer.validated_data.get('user_type', 'customer'),
                    auth_provider='phone',
                    is_verified=True
                )
                created = True
            
            # Update verification status if user already exists
            if not created and not user.is_verified:
                user.is_verified = True
                user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'OTP verified successfully',
                'created': created,
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginView(APIView):
    """Google OAuth login"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            google_data = serializer.validated_data['token']
            user_type = serializer.validated_data.get('user_type', 'customer')
            
            email = google_data.get('email')
            google_id = google_data.get('sub')
            first_name = google_data.get('given_name', '')
            last_name = google_data.get('family_name', '')
            picture = google_data.get('picture', '')
            
            if not email:
                return Response({
                    'error': 'Email not provided by Google'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user exists by email or create new
            try:
                user = User.objects.get(email=email)
                created = False
                
                # Update auth provider if it was phone before
                if user.auth_provider != 'google':
                    user.auth_provider = 'google'
                    user.save()
                    
            except User.DoesNotExist:
                # Create phone from google_id (or use email as identifier)
                phone = f"+{google_id[:13]}"  # Use part of Google ID as phone placeholder
                
                user = User.objects.create_user(
                    phone=phone,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=user_type,
                    auth_provider='google',
                    is_verified=True
                )
                created = True
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'created': created,
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View and update user profile"""
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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'user': UserSerializer(self.get_object()).data,
            'message': 'Profile updated successfully'
        })


class ChangePasswordView(APIView):
    """Change user password"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """List all users (Admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = User.objects.all()
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user (Admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def logout_view(request):
    """Logout user by blacklisting refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
