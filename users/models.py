from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for phone-based authentication"""
    
    def create_user(self, phone, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required')
        
        user = self.model(phone=phone, **extra_fields)
        user.set_unusable_password()  # No password needed
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(phone, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Simplified User model - Phone OTP and Google Auth only"""
    
    phone = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(
            r'^\+?[1-9]\d{1,14}$',
            'Enter a valid phone number with country code (E.164 format)'
        )],
        help_text='Phone number with country code (e.g., +1234567890)'
    )
    google_uid = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text='Google User ID for Google Sign-In'
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Optional fields for user profile
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['google_uid']),
        ]
    
    def __str__(self):
        return self.phone
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.phone
