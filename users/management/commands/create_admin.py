from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Create a superuser with password'

    def handle(self, *args, **options):
        phone = '+8801897345672'
        password = 'admin123'
        
        # Delete existing user if exists
        User.objects.filter(phone=phone).delete()
        
        # Create new superuser
        user = User.objects.create_superuser(
            phone=phone,
            password=password
        )
        
        self.stdout.write(self.style.SUCCESS(f'Superuser created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Phone: {phone}'))
        self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
        self.stdout.write(self.style.SUCCESS(f'Login at: http://localhost:8000/admin/'))
