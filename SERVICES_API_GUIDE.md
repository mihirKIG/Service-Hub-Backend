# Services & Bookings API Guide

This guide covers the comprehensive REST API for Services and Bookings in the ServiceHub platform.

## Services API

Base URL: `/api/services/`

### Endpoints

#### 1. List Services
```
GET /api/services/
```
**Permission:** Public (AllowAny)

**Query Parameters:**
- `category` - Filter by category ID
- `pricing_type` - Filter by pricing type (hourly, fixed, package)
- `status` - Filter by status (active, inactive, draft)
- `is_remote` - Filter by remote availability (true/false)
- `is_onsite` - Filter by onsite availability (true/false)
- `provider` - Filter by provider ID
- `min_price` - Minimum base price
- `max_price` - Maximum base price
- `search` - Search in title, description, provider name
- `ordering` - Order by field (created_at, base_price, views_count, bookings_count, title)
  - Prefix with `-` for descending order (e.g., `-created_at`)

**Example:**
```bash
GET /api/services/?category=1&pricing_type=hourly&ordering=-views_count
```

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/services/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Professional Plumbing Service",
      "short_description": "Expert plumbing repairs and installations",
      "pricing_type": "hourly",
      "base_price": "50.00",
      "hourly_rate": "50.00",
      "duration_minutes": 60,
      "is_remote": false,
      "is_onsite": true,
      "status": "active",
      "image": "/media/services/plumbing.jpg",
      "views_count": 150,
      "bookings_count": 25,
      "provider_name": "ABC Plumbing Co.",
      "provider_rating": 4.8,
      "category_name": "Plumbing",
      "average_rating": 4.7,
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-07T15:30:00Z"
    }
  ]
}
```

#### 2. Get Service Details
```
GET /api/services/{id}/
```
**Permission:** Public (AllowAny)

**Response:**
```json
{
  "id": 1,
  "provider": {
    "id": 1,
    "business_name": "ABC Plumbing Co.",
    "bio": "Professional plumbing services...",
    "rating": 4.8,
    "total_reviews": 45,
    "hourly_rate": "50.00"
  },
  "category": {
    "id": 1,
    "name": "Plumbing",
    "description": "Plumbing services",
    "icon": "/media/category_icons/plumbing.png"
  },
  "title": "Professional Plumbing Service",
  "description": "We provide comprehensive plumbing services...",
  "short_description": "Expert plumbing repairs and installations",
  "pricing_type": "hourly",
  "base_price": "50.00",
  "hourly_rate": "50.00",
  "duration_minutes": 60,
  "is_remote": false,
  "is_onsite": true,
  "status": "active",
  "min_booking_hours": 24,
  "max_bookings_per_day": 5,
  "image": "/media/services/plumbing.jpg",
  "images": [
    {
      "id": 1,
      "image": "/media/services/gallery/img1.jpg",
      "caption": "Recent work",
      "order": 0
    }
  ],
  "faqs": [
    {
      "id": 1,
      "question": "Do you provide emergency services?",
      "answer": "Yes, we offer 24/7 emergency plumbing services.",
      "order": 0
    }
  ],
  "views_count": 150,
  "bookings_count": 25,
  "average_rating": 4.7,
  "created_at": "2026-01-01T10:00:00Z",
  "updated_at": "2026-01-07T15:30:00Z"
}
```

#### 3. Create Service
```
POST /api/services/
```
**Permission:** Authenticated users with provider profile

**Request Body:**
```json
{
  "category": 1,
  "title": "Professional Plumbing Service",
  "description": "We provide comprehensive plumbing services including repairs, installations, and maintenance.",
  "short_description": "Expert plumbing repairs and installations",
  "pricing_type": "hourly",
  "base_price": "50.00",
  "hourly_rate": "50.00",
  "duration_minutes": 60,
  "is_remote": false,
  "is_onsite": true,
  "status": "active",
  "min_booking_hours": 24,
  "max_bookings_per_day": 5,
  "image": "<file>",
  "faqs": [
    {
      "question": "Do you provide emergency services?",
      "answer": "Yes, we offer 24/7 emergency plumbing services.",
      "order": 0
    }
  ]
}
```

#### 4. Update Service
```
PUT /api/services/{id}/
PATCH /api/services/{id}/
```
**Permission:** Service owner (provider who created the service)

**Request Body:** Same as create (partial update for PATCH)

#### 5. Delete Service
```
DELETE /api/services/{id}/
```
**Permission:** Service owner

#### 6. Featured Services
```
GET /api/services/featured/
```
**Permission:** Public

Returns top 10 services with highest bookings and views.

#### 7. Popular Services
```
GET /api/services/popular/
```
**Permission:** Public

Returns top 10 services by view count.

#### 8. My Services
```
GET /api/services/my_services/
```
**Permission:** Authenticated provider

Returns all services created by the authenticated provider.

#### 9. Add Service Image
```
POST /api/services/{id}/add_image/
```
**Permission:** Service owner

**Request Body:**
```json
{
  "image": "<file>",
  "caption": "Recent work",
  "order": 0
}
```

#### 10. Add Service FAQ
```
POST /api/services/{id}/add_faq/
```
**Permission:** Service owner

**Request Body:**
```json
{
  "question": "What is your cancellation policy?",
  "answer": "We require 24 hours notice for cancellations.",
  "order": 1
}
```

#### 11. Remove Service Image
```
DELETE /api/services/{id}/remove_image/
```
**Permission:** Service owner

**Request Body:**
```json
{
  "image_id": 5
}
```

#### 12. Remove Service FAQ
```
DELETE /api/services/{id}/remove_faq/
```
**Permission:** Service owner

**Request Body:**
```json
{
  "faq_id": 3
}
```

---

## Bookings API

Base URL: `/api/bookings/`

### Endpoints

#### 1. List Bookings
```
GET /api/bookings/
```
**Permission:** Authenticated users

Returns bookings for the authenticated user:
- For customers: bookings they created
- For providers: bookings assigned to them

**Query Parameters:**
- `status` - Filter by status (pending, confirmed, in_progress, completed, cancelled, refunded)
- `start_date` - Filter by booking date (from)
- `end_date` - Filter by booking date (to)
- `search` - Search in service title, description, city
- `ordering` - Order by booking_date, created_at, total_amount

**Example:**
```bash
GET /api/bookings/?status=confirmed&start_date=2026-01-01&ordering=-booking_date
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "customer": {
        "id": 2,
        "email": "customer@example.com",
        "full_name": "John Doe"
      },
      "provider": {
        "id": 1,
        "business_name": "ABC Plumbing Co.",
        "rating": 4.8
      },
      "service_title": "Emergency Pipe Repair",
      "service_description": "Fix leaking pipe in kitchen",
      "booking_date": "2026-01-15",
      "start_time": "10:00:00",
      "end_time": "12:00:00",
      "duration_hours": "2.00",
      "service_address": "123 Main St",
      "city": "New York",
      "postal_code": "10001",
      "hourly_rate": "50.00",
      "total_amount": "100.00",
      "status": "confirmed",
      "created_at": "2026-01-07T10:00:00Z",
      "attachments": []
    }
  ]
}
```

#### 2. Get Booking Details
```
GET /api/bookings/{id}/
```
**Permission:** Customer or Provider associated with the booking

#### 3. Create Booking
```
POST /api/bookings/
```
**Permission:** Authenticated users

**Request Body:**
```json
{
  "provider_id": 1,
  "service_title": "Emergency Pipe Repair",
  "service_description": "Fix leaking pipe in kitchen",
  "booking_date": "2026-01-15",
  "start_time": "10:00:00",
  "end_time": "12:00:00",
  "duration_hours": "2.00",
  "service_address": "123 Main St",
  "city": "New York",
  "postal_code": "10001",
  "customer_notes": "Please call upon arrival"
}
```

#### 4. Update Booking Status
```
PATCH /api/bookings/{id}/
```
**Permission:** Customer or Provider associated with the booking

**Request Body:**
```json
{
  "status": "confirmed"
}
```

**Valid Status Transitions:**
- Customer can: cancel pending/confirmed bookings
- Provider can: confirm pending, start confirmed, complete in_progress

#### 5. Cancel Booking
```
POST /api/bookings/{id}/cancel/
```
**Permission:** Customer or Provider associated with the booking

**Request Body:**
```json
{
  "cancellation_reason": "Schedule conflict"
}
```

**Note:** Only pending or confirmed bookings can be cancelled.

#### 6. Upcoming Bookings
```
GET /api/bookings/upcoming/
```
**Permission:** Authenticated users

Returns next 5 upcoming bookings (pending or confirmed) for the user.

**Response:**
```json
[
  {
    "id": 1,
    "service_title": "Emergency Pipe Repair",
    "booking_date": "2026-01-15",
    "start_time": "10:00:00",
    "status": "confirmed",
    "provider": {...}
  }
]
```

#### 7. Booking Statistics
```
GET /api/bookings/stats/
```
**Permission:** Authenticated users

Returns booking statistics for the user.

**Response (for Providers):**
```json
{
  "total_bookings": 150,
  "completed_bookings": 135,
  "completion_rate": 90.0,
  "pending_bookings": 5,
  "confirmed_bookings": 10
}
```

**Response (for Customers):**
```json
{
  "total_bookings": 25,
  "completed_bookings": 20,
  "pending_bookings": 2,
  "cancelled_bookings": 3
}
```

#### 8. Booking Attachments

##### List/Create Attachments
```
GET /api/bookings/{booking_id}/attachments/
POST /api/bookings/{booking_id}/attachments/
```
**Permission:** Customer or Provider associated with the booking

**POST Request Body:**
```json
{
  "file": "<file>",
  "description": "Before photo"
}
```

##### Get/Delete Attachment
```
GET /api/bookings/{booking_id}/attachments/{id}/
DELETE /api/bookings/{booking_id}/attachments/{id}/
```
**Permission:** Customer or Provider associated with the booking

---

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Resource deleted successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Rate Limiting

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour

## Example Usage

### JavaScript (Fetch API)

```javascript
// List services
fetch('http://localhost:8000/api/services/?category=1', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));

// Create booking (authenticated)
fetch('http://localhost:8000/api/bookings/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: JSON.stringify({
    provider_id: 1,
    service_title: "Emergency Repair",
    booking_date: "2026-01-15",
    start_time: "10:00:00",
    end_time: "12:00:00",
    duration_hours: "2.00",
    service_address: "123 Main St",
    city: "New York",
    postal_code: "10001"
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python (requests)

```python
import requests

# List services
response = requests.get('http://localhost:8000/api/services/', params={
    'category': 1,
    'ordering': '-views_count'
})
services = response.json()

# Create service (authenticated)
headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
}
data = {
    'category': 1,
    'title': 'Professional Service',
    'description': 'Service description',
    'pricing_type': 'hourly',
    'base_price': '50.00',
    'hourly_rate': '50.00',
    'status': 'active'
}
response = requests.post('http://localhost:8000/api/services/', 
                        headers=headers, json=data)
service = response.json()
```

## Best Practices

1. **Always validate data** on the frontend before sending requests
2. **Handle errors gracefully** with try-catch blocks
3. **Use pagination** for list endpoints to improve performance
4. **Cache frequently accessed data** like service categories
5. **Implement retry logic** for network failures
6. **Use appropriate HTTP methods** (GET for reading, POST for creating, etc.)
7. **Keep JWT tokens secure** and refresh them before expiration
