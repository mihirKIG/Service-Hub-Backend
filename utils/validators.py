"""
Custom validators
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
import re


def validate_phone_number(value):
    """
    Validate phone number format
    Accepts formats: +1234567890, 1234567890, +1-234-567-8900
    """
    pattern = r'^\+?1?\d{9,15}$'
    cleaned = re.sub(r'[-\s()]', '', value)
    
    if not re.match(pattern, cleaned):
        raise ValidationError(
            'Invalid phone number format. Please enter a valid phone number.',
            params={'value': value},
        )


def validate_future_date(value):
    """
    Validate that date is in the future
    """
    if value < timezone.now().date():
        raise ValidationError(
            'Date must be in the future.',
            params={'value': value},
        )


def validate_future_datetime(value):
    """
    Validate that datetime is in the future
    """
    if value < timezone.now():
        raise ValidationError(
            'Date and time must be in the future.',
            params={'value': value},
        )


def validate_business_hours(start_time, end_time):
    """
    Validate business hours (start time before end time)
    """
    if start_time >= end_time:
        raise ValidationError('End time must be after start time.')


def validate_rating(value):
    """
    Validate rating is between 1 and 5
    """
    if not 1 <= value <= 5:
        raise ValidationError(
            'Rating must be between 1 and 5.',
            params={'value': value},
        )


def validate_postal_code(value):
    """
    Validate US postal code format
    Accepts: 12345 or 12345-6789
    """
    pattern = r'^\d{5}(-\d{4})?$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            'Invalid postal code format. Use format: 12345 or 12345-6789',
            params={'value': value},
        )


def validate_file_size(file, max_size_mb=5):
    """
    Validate file size
    
    Args:
        file: File object
        max_size_mb: Maximum file size in megabytes (default 5MB)
    """
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f'File size must not exceed {max_size_mb}MB.',
            params={'size': file.size},
        )


def validate_image_file(file):
    """
    Validate image file type
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_extension = file.name.lower().split('.')[-1]
    
    if f'.{file_extension}' not in valid_extensions:
        raise ValidationError(
            f'Invalid file type. Allowed types: {", ".join(valid_extensions)}',
            params={'extension': file_extension},
        )


def validate_document_file(file):
    """
    Validate document file type
    """
    valid_extensions = ['.pdf', '.doc', '.docx', '.txt']
    file_extension = file.name.lower().split('.')[-1]
    
    if f'.{file_extension}' not in valid_extensions:
        raise ValidationError(
            f'Invalid file type. Allowed types: {", ".join(valid_extensions)}',
            params={'extension': file_extension},
        )


def validate_username(value):
    """
    Validate username format
    Only alphanumeric and underscores, 3-30 characters
    """
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            'Username must be 3-30 characters and contain only letters, numbers, and underscores.',
            params={'value': value},
        )


def validate_strong_password(value):
    """
    Validate strong password
    At least 8 characters, one uppercase, one lowercase, one number
    """
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Password must contain at least one uppercase letter.')
    
    if not re.search(r'[a-z]', value):
        raise ValidationError('Password must contain at least one lowercase letter.')
    
    if not re.search(r'\d', value):
        raise ValidationError('Password must contain at least one number.')
