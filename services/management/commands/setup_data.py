from django.core.management.base import BaseCommand
from providers.models import ServiceCategory, Provider
from users.models import User


class Command(BaseCommand):
    help = 'Create sample categories and provider for testing'

    def handle(self, *args, **options):
        # Create Service Categories
        categories_data = [
            {'name': 'Plumbing', 'description': 'Professional plumbing services'},
            {'name': 'Electrical', 'description': 'Electrical repair and installation'},
            {'name': 'Carpentry', 'description': 'Woodwork and carpentry services'},
            {'name': 'Cleaning', 'description': 'Home and office cleaning services'},
            {'name': 'Painting', 'description': 'Interior and exterior painting'},
            {'name': 'HVAC', 'description': 'Heating, ventilation, and air conditioning'},
            {'name': 'Landscaping', 'description': 'Lawn care and landscaping'},
            {'name': 'Pest Control', 'description': 'Pest control and extermination'},
        ]
        
        created_categories = []
        for cat_data in categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description'], 'is_active': True}
            )
            if created:
                created_categories.append(category.name)
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: {category.name}'))
            else:
                self.stdout.write(f'  Category already exists: {category.name}')
        
        # Create a demo provider if one doesn't exist
        if not Provider.objects.exists():
            # Get or create a user for the provider
            phone = '+1234567890'
            user, user_created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    'first_name': 'Demo',
                    'last_name': 'Provider',
                    'is_verified': True,
                    'is_active': True
                }
            )
            
            if user_created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created demo user: {phone}'))
            
            # Create provider profile
            provider = Provider.objects.create(
                user=user,
                business_name='Demo Service Provider',
                bio='Professional service provider offering quality services',
                experience_years=5,
                hourly_rate='50.00',
                city='New York',
                state='NY',
                country='USA',
                postal_code='10001',
                status='approved',
                is_available=True
            )
            
            # Add some categories to the provider
            if ServiceCategory.objects.exists():
                provider.categories.add(*ServiceCategory.objects.all()[:3])
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created demo provider: {provider.business_name}'))
        else:
            self.stdout.write('  Provider already exists')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Setup Complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'Categories created: {len(created_categories)}')
        self.stdout.write(f'Total categories: {ServiceCategory.objects.count()}')
        self.stdout.write(f'Total providers: {Provider.objects.count()}')
        self.stdout.write('')
        self.stdout.write('You can now add services in the admin panel!')
        self.stdout.write('Visit: http://localhost:8000/admin/services/service/add/')
