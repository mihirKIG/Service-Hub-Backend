# ServiceHub - Service Marketplace Platform

A comprehensive Django REST API backend for a service marketplace platform connecting service providers with customers.

## Features

### User Management
- Custom user authentication with JWT tokens
- Support for multiple user types (Customer, Provider, Admin)
- Profile management with image upload
- Email and phone verification
- Password reset functionality

### Provider Management
- Provider profiles with business information
- Service categories and pricing
- Availability scheduling
- Portfolio/work samples
- Rating and verification system
- Location-based search

### Booking System
- Service booking with date/time selection
- Booking status management (pending, confirmed, in_progress, completed, cancelled)
- Booking attachments
- Calendar integration
- Automated reminders

### Payment Processing
- Multiple payment methods support
- Stripe integration
- Payment history and receipts
- Refund processing
- Saved payment methods
- Transaction logging

### Reviews & Ratings
- 5-star rating system
- Detailed reviews with sub-ratings
- Provider responses
- Review images
- Helpful vote tracking
- Review moderation

### Notifications
- In-app notifications
- Email notifications
- SMS notifications
- Push notifications
- Customizable notification preferences
- Real-time updates

### Real-time Chat
- WebSocket-based chat system
- One-on-one messaging
- Message read receipts
- Typing indicators
- File attachments
- Online/offline status

## Tech Stack

- **Framework:** Django 5.0 + Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT (Simple JWT)
- **Real-time:** Django Channels + Redis
- **Task Queue:** Celery
- **Payment:** Stripe
- **SMS:** Twilio
- **API Documentation:** drf-yasg (Swagger/OpenAPI)

## Project Structure

```
servicehub/
├── servicehub_backend/      # Main project configuration
├── users/                   # User authentication & management
├── providers/               # Service provider profiles
├── bookings/               # Booking management
├── payments/               # Payment processing
├── reviews/                # Reviews & ratings
├── notifications/          # Notification system
├── chat/                   # Real-time messaging
├── utils/                  # Shared utilities
├── media/                  # Uploaded files
├── static/                 # Static files
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Redis 6+

### Setup Steps

1. **Clone the repository**
   ```bash
   cd servicehub
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb servicehub_db
   
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run Development Server**
   ```bash
   # HTTP Server
   python manage.py runserver
   
   # WebSocket Server (in another terminal)
   daphne -b 0.0.0.0 -p 8001 servicehub_backend.asgi:application
   ```

9. **Start Celery Worker (optional)**
   ```bash
   celery -A servicehub_backend worker -l info
   ```

10. **Start Redis (required for WebSockets)**
    ```bash
    redis-server
    ```

## API Documentation

Once the server is running, access the API documentation at:

- **Swagger UI:** http://localhost:8000/swagger/
- **ReDoc:** http://localhost:8000/redoc/

## API Endpoints

### Authentication
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `POST /api/users/token/refresh/` - Refresh JWT token
- `POST /api/users/logout/` - User logout

### Users
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update user profile
- `POST /api/users/change-password/` - Change password

### Providers
- `GET /api/providers/` - List providers
- `POST /api/providers/create/` - Create provider profile
- `GET /api/providers/{id}/` - Get provider details
- `GET /api/providers/categories/` - List service categories

### Bookings
- `GET /api/bookings/` - List bookings
- `POST /api/bookings/create/` - Create booking
- `GET /api/bookings/{id}/` - Get booking details
- `PUT /api/bookings/{id}/update/` - Update booking status
- `POST /api/bookings/{id}/cancel/` - Cancel booking

### Payments
- `GET /api/payments/` - List payments
- `POST /api/payments/create/` - Process payment
- `POST /api/payments/{id}/refund/` - Request refund

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/create/` - Create review
- `GET /api/reviews/{id}/` - Get review details
- `GET /api/reviews/provider/{provider_id}/` - Get provider reviews

### Notifications
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/unread-count/` - Get unread count
- `POST /api/notifications/mark-all-read/` - Mark all as read

### Chat
- `GET /api/chat/rooms/` - List chat rooms
- `POST /api/chat/rooms/create/` - Create chat room
- `GET /api/chat/rooms/{id}/messages/` - Get messages
- `POST /api/chat/rooms/{id}/messages/send/` - Send message
- `WS /ws/chat/{chatroom_id}/` - WebSocket connection

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test providers

# With pytest
pytest
```

## Deployment

### Production Checklist

1. Set `DEBUG=False` in settings
2. Configure proper `SECRET_KEY`
3. Set up production database
4. Configure HTTPS
5. Set up proper CORS settings
6. Configure email backend
7. Set up file storage (AWS S3, etc.)
8. Configure Redis for production
9. Set up Celery with supervisor
10. Configure logging and monitoring

### Environment Variables

All sensitive configuration should be in environment variables (see `.env.example`).

## Security

- JWT authentication for API access
- CORS configuration for frontend integration
- Rate limiting on sensitive endpoints
- Input validation and sanitization
- SQL injection prevention (Django ORM)
- XSS protection
- CSRF protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support, email support@servicehub.com or create an issue in the repository.

## Authors

- ServiceHub Development Team

## Acknowledgments

- Django REST Framework
- Django Channels
- All contributors and open-source projects used
