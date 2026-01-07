# ServiceHub Platform - Complete API Documentation for Frontend

> **Last Updated:** January 7, 2026  
> **Base URL:** `http://localhost:8000`  
> **API Version:** v1

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Modules](#api-modules)
4. [Data Models](#data-models)
5. [Frontend Integration Guide](#frontend-integration-guide)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)

---

## Overview

ServiceHub is a comprehensive platform connecting service providers with customers. The backend provides RESTful APIs for:

- ✅ User Authentication (Phone OTP & Google OAuth)
- ✅ Provider Management
- ✅ Service Listings
- ✅ Booking System
- ✅ Payment Processing
- ✅ Reviews & Ratings
- ✅ Real-time Chat
- ✅ Notifications

---

## Authentication

### Available Methods

1. **Phone OTP Authentication**
2. **Google OAuth**
3. **JWT Token Management**

### 1. Phone OTP Authentication

#### Send OTP
```http
POST /api/users/send-otp/
```

**Request Body:**
```json
{
  "phone_number": "+1234567890"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully",
  "phone_number": "+1234567890"
}
```

#### Verify OTP
```http
POST /api/users/verify-otp/
```

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "otp": "123456"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "phone_number": "+1234567890",
    "full_name": "John Doe",
    "user_type": "customer",
    "is_verified": true
  }
}
```

### 2. Google OAuth

```http
POST /api/users/google/
```

**Request Body:**
```json
{
  "token": "google_oauth_token_here"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@gmail.com",
    "full_name": "John Doe",
    "user_type": "customer"
  }
}
```

### 3. Token Management

#### Refresh Token
```http
POST /api/users/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "new_access_token_here"
}
```

#### Logout
```http
POST /api/users/logout/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. User Profile

#### Get Profile
```http
GET /api/users/profile/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "phone_number": "+1234567890",
  "full_name": "John Doe",
  "user_type": "customer",
  "profile_picture": "/media/profiles/user1.jpg",
  "date_of_birth": "1990-01-01",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "postal_code": "10001",
  "is_verified": true,
  "date_joined": "2026-01-01T10:00:00Z"
}
```

#### Update Profile
```http
PUT /api/users/profile/
PATCH /api/users/profile/
```

**Request Body:**
```json
{
  "full_name": "John Doe Updated",
  "address": "456 New St",
  "city": "Los Angeles"
}
```

---

## API Modules

## 1. Providers API

Base URL: `/api/providers/`

### Service Categories

#### List Categories
```http
GET /api/providers/categories/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Plumbing",
    "description": "Professional plumbing services",
    "icon": "/media/category_icons/plumbing.png",
    "is_active": true
  }
]
```

#### Get Category Details
```http
GET /api/providers/categories/{id}/
```

### Provider Listings

#### List Providers
```http
GET /api/providers/
```

**Query Parameters:**
- `search` - Search by business name, bio
- `category` - Filter by category ID
- `city` - Filter by city
- `min_rate` - Minimum hourly rate
- `max_rate` - Maximum hourly rate
- `min_rating` - Minimum rating
- `sort_by` - Sort by: `rating`, `name`, `experience`, `hourly_rate`

**Example:**
```http
GET /api/providers/?category=1&city=New York&sort_by=rating
```

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/providers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "business_name": "ABC Plumbing Co.",
      "bio": "Professional plumbing services...",
      "categories": [
        {
          "id": 1,
          "name": "Plumbing"
        }
      ],
      "experience_years": 10,
      "hourly_rate": "50.00",
      "city": "New York",
      "state": "NY",
      "rating": 4.8,
      "total_reviews": 45,
      "total_bookings": 150,
      "status": "approved",
      "profile_picture": "/media/providers/profile1.jpg"
    }
  ]
}
```

#### Get Provider Details
```http
GET /api/providers/{id}/
```

**Response:**
```json
{
  "id": 1,
  "user": {
    "id": 5,
    "email": "provider@example.com",
    "full_name": "Jane Provider"
  },
  "business_name": "ABC Plumbing Co.",
  "bio": "We provide professional plumbing services...",
  "categories": [...],
  "experience_years": 10,
  "hourly_rate": "50.00",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "postal_code": "10001",
  "latitude": "40.7128",
  "longitude": "-74.0060",
  "rating": 4.8,
  "total_reviews": 45,
  "total_bookings": 150,
  "completed_bookings": 140,
  "completion_rate": 93.33,
  "certifications": "Licensed Plumber #12345",
  "insurance_details": "Fully insured",
  "website": "https://abcplumbing.com",
  "social_media": {
    "facebook": "abcplumbing",
    "instagram": "abcplumbing"
  },
  "status": "approved",
  "portfolio": [...],
  "availability": [...]
}
```

#### Create Provider Profile
```http
POST /api/providers/create/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "business_name": "My Service Business",
  "bio": "Professional services provider...",
  "categories": [1, 2],
  "experience_years": 5,
  "hourly_rate": "45.00",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "postal_code": "10001",
  "certifications": "Licensed #12345",
  "insurance_details": "Fully insured"
}
```

#### Update Provider Profile
```http
PUT /api/providers/me/update/
PATCH /api/providers/me/update/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

#### Get My Provider Profile
```http
GET /api/providers/me/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

### Provider Availability

#### List Availability
```http
GET /api/providers/availability/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "day_of_week": 0,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "is_available": true
  }
]
```

#### Create/Update Availability
```http
POST /api/providers/availability/
PUT /api/providers/availability/{id}/
```

### Provider Portfolio

#### List Portfolio Items
```http
GET /api/providers/portfolio/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Kitchen Renovation",
    "description": "Complete kitchen plumbing installation",
    "image": "/media/portfolio/kitchen1.jpg",
    "project_date": "2025-12-01",
    "created_at": "2026-01-01T10:00:00Z"
  }
]
```

#### Add Portfolio Item
```http
POST /api/providers/portfolio/
```

**Request Body (multipart/form-data):**
```json
{
  "title": "Project Title",
  "description": "Project description",
  "image": "<file>",
  "project_date": "2025-12-01"
}
```

---

## 2. Services API

Base URL: `/api/services/`

### List Services
```http
GET /api/services/
```

**Query Parameters:**
- `category` - Category ID
- `pricing_type` - `hourly`, `fixed`, `package`
- `status` - `active`, `inactive`, `draft`
- `is_remote` - `true`, `false`
- `is_onsite` - `true`, `false`
- `provider` - Provider ID
- `min_price` - Minimum price
- `max_price` - Maximum price
- `search` - Search in title, description
- `ordering` - `-created_at`, `base_price`, `-views_count`, `-bookings_count`

**Example:**
```http
GET /api/services/?category=1&pricing_type=hourly&ordering=-views_count
```

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "title": "Professional Plumbing Service",
      "short_description": "Expert repairs and installations",
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
      "created_at": "2026-01-01T10:00:00Z"
    }
  ]
}
```

### Get Service Details
```http
GET /api/services/{id}/
```

**Response:**
```json
{
  "id": 1,
  "provider": {
    "id": 1,
    "business_name": "ABC Plumbing Co.",
    "rating": 4.8,
    "hourly_rate": "50.00"
  },
  "category": {
    "id": 1,
    "name": "Plumbing"
  },
  "title": "Professional Plumbing Service",
  "description": "Complete service description...",
  "short_description": "Expert repairs",
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
      "caption": "Recent work"
    }
  ],
  "faqs": [
    {
      "id": 1,
      "question": "Do you provide emergency services?",
      "answer": "Yes, 24/7 available"
    }
  ],
  "views_count": 150,
  "bookings_count": 25,
  "average_rating": 4.7
}
```

### Featured Services
```http
GET /api/services/featured/
```

Returns top 10 services by bookings and views.

### Popular Services
```http
GET /api/services/popular/
```

Returns top 10 services by views.

### My Services (Provider)
```http
GET /api/services/my_services/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

### Create Service (Provider)
```http
POST /api/services/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "category": 1,
  "title": "Professional Service",
  "description": "Full description",
  "short_description": "Short description",
  "pricing_type": "hourly",
  "base_price": "50.00",
  "hourly_rate": "50.00",
  "duration_minutes": 60,
  "is_remote": false,
  "is_onsite": true,
  "status": "active",
  "min_booking_hours": 24,
  "max_bookings_per_day": 5
}
```

### Update/Delete Service
```http
PUT /api/services/{id}/
PATCH /api/services/{id}/
DELETE /api/services/{id}/
```

---

## 3. Bookings API

Base URL: `/api/bookings/`

### List Bookings
```http
GET /api/bookings/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` - `pending`, `confirmed`, `in_progress`, `completed`, `cancelled`
- `start_date` - YYYY-MM-DD
- `end_date` - YYYY-MM-DD
- `search` - Search term
- `ordering` - `-booking_date`, `total_amount`

**Response:**
```json
{
  "count": 10,
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
      "service_description": "Fix leaking pipe",
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
      "created_at": "2026-01-07T10:00:00Z"
    }
  ]
}
```

### Create Booking
```http
POST /api/bookings/create/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "provider_id": 1,
  "service_title": "Emergency Repair",
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

### Get Booking Details
```http
GET /api/bookings/{id}/
```

### Update Booking
```http
PATCH /api/bookings/{id}/update/
```

**Request Body:**
```json
{
  "status": "confirmed"
}
```

### Cancel Booking
```http
POST /api/bookings/{id}/cancel/
```

**Request Body:**
```json
{
  "cancellation_reason": "Schedule conflict"
}
```

### Upcoming Bookings
```http
GET /api/bookings/upcoming/
```

Returns next 5 upcoming bookings.

### Booking Statistics
```http
GET /api/bookings/stats/
```

**Response (Provider):**
```json
{
  "total_bookings": 150,
  "completed_bookings": 135,
  "completion_rate": 90.0,
  "pending_bookings": 5,
  "confirmed_bookings": 10
}
```

**Response (Customer):**
```json
{
  "total_bookings": 25,
  "completed_bookings": 20,
  "pending_bookings": 2,
  "cancelled_bookings": 3
}
```

---

## 4. Reviews API

Base URL: `/api/reviews/`

### List Reviews
```http
GET /api/reviews/
```

**Query Parameters:**
- `provider` - Provider ID
- `rating` - Filter by rating (1-5)
- `ordering` - `-created_at`, `rating`

### Get Provider Reviews
```http
GET /api/reviews/provider/{provider_id}/
```

**Response:**
```json
{
  "count": 45,
  "results": [
    {
      "id": 1,
      "customer": {
        "id": 2,
        "full_name": "John Doe"
      },
      "provider": 1,
      "booking": 5,
      "rating": 5,
      "comment": "Excellent service!",
      "images": [
        {
          "id": 1,
          "image": "/media/reviews/img1.jpg"
        }
      ],
      "response": {
        "response": "Thank you for your feedback!",
        "responded_at": "2026-01-08T10:00:00Z"
      },
      "helpful_count": 10,
      "created_at": "2026-01-07T15:00:00Z"
    }
  ]
}
```

### Get Provider Review Stats
```http
GET /api/reviews/provider/{provider_id}/stats/
```

**Response:**
```json
{
  "average_rating": 4.8,
  "total_reviews": 45,
  "rating_distribution": {
    "5": 30,
    "4": 10,
    "3": 3,
    "2": 1,
    "1": 1
  },
  "recent_reviews": [...]
}
```

### Create Review
```http
POST /api/reviews/create/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "provider": 1,
  "booking": 5,
  "rating": 5,
  "comment": "Great service!",
  "service_quality": 5,
  "professionalism": 5,
  "value_for_money": 4,
  "punctuality": 5
}
```

### Update Review
```http
PUT /api/reviews/{id}/update/
```

### Delete Review
```http
DELETE /api/reviews/{id}/delete/
```

### Mark Review Helpful
```http
POST /api/reviews/{id}/helpful/
```

### Add Review Response (Provider)
```http
POST /api/reviews/{review_id}/response/
```

**Request Body:**
```json
{
  "response": "Thank you for your feedback!"
}
```

### My Reviews
```http
GET /api/reviews/my-reviews/
```

---

## 5. Payments API

Base URL: `/api/payments/`

### List Payments
```http
GET /api/payments/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` - `pending`, `completed`, `failed`, `refunded`
- `payment_method` - `credit_card`, `debit_card`, `paypal`, `bank_transfer`

**Response:**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "booking": {
        "id": 5,
        "service_title": "Plumbing Repair"
      },
      "amount": "100.00",
      "payment_method": "credit_card",
      "status": "completed",
      "transaction_id": "txn_12345",
      "paid_at": "2026-01-07T10:00:00Z",
      "created_at": "2026-01-07T09:55:00Z"
    }
  ]
}
```

### Create Payment
```http
POST /api/payments/create/
```

**Request Body:**
```json
{
  "booking": 5,
  "amount": "100.00",
  "payment_method": "credit_card",
  "payment_details": {
    "card_number": "****1234",
    "card_holder": "John Doe"
  }
}
```

### Get Payment Details
```http
GET /api/payments/{id}/
```

### Process Refund
```http
POST /api/payments/{id}/refund/
```

**Request Body:**
```json
{
  "reason": "Service cancelled",
  "amount": "100.00"
}
```

### Payment Statistics
```http
GET /api/payments/stats/
```

**Response:**
```json
{
  "total_payments": 150,
  "total_amount": "7500.00",
  "pending_amount": "200.00",
  "refunded_amount": "100.00",
  "this_month_earnings": "1500.00"
}
```

### Payment Methods

#### List Payment Methods
```http
GET /api/payments/methods/
```

#### Add Payment Method
```http
POST /api/payments/methods/
```

**Request Body:**
```json
{
  "method_type": "credit_card",
  "card_number": "4111111111111111",
  "card_holder_name": "John Doe",
  "expiry_date": "12/25",
  "is_default": true
}
```

---

## 6. Notifications API

Base URL: `/api/notifications/`

### List Notifications
```http
GET /api/notifications/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `is_read` - `true`, `false`
- `notification_type` - `booking`, `payment`, `review`, `message`, `system`

**Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "title": "New Booking Received",
      "message": "You have a new booking request from John Doe",
      "notification_type": "booking",
      "is_read": false,
      "data": {
        "booking_id": 5
      },
      "created_at": "2026-01-07T10:00:00Z"
    }
  ]
}
```

### Get Unread Count
```http
GET /api/notifications/unread-count/
```

**Response:**
```json
{
  "unread_count": 5
}
```

### Mark Notification as Read
```http
POST /api/notifications/{id}/mark-read/
```

### Mark All as Read
```http
POST /api/notifications/mark-all-read/
```

### Delete Notification
```http
DELETE /api/notifications/{id}/delete/
```

### Clear All Notifications
```http
DELETE /api/notifications/clear-all/
```

### Notification Preferences
```http
GET /api/notifications/preferences/
PUT /api/notifications/preferences/
```

**Response/Request Body:**
```json
{
  "email_notifications": true,
  "push_notifications": true,
  "sms_notifications": false,
  "booking_notifications": true,
  "payment_notifications": true,
  "review_notifications": true,
  "message_notifications": true
}
```

---

## 7. Chat API

Base URL: `/api/chat/`

### List Chat Rooms
```http
GET /api/chat/rooms/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "customer": {
        "id": 2,
        "full_name": "John Doe"
      },
      "provider": {
        "id": 1,
        "business_name": "ABC Plumbing Co."
      },
      "last_message": {
        "message": "Thanks for the update",
        "created_at": "2026-01-07T15:30:00Z"
      },
      "unread_count": 2,
      "created_at": "2026-01-05T10:00:00Z"
    }
  ]
}
```

### Create Chat Room
```http
POST /api/chat/rooms/create/
```

**Request Body:**
```json
{
  "provider": 1
}
```

### Get Chat Room Details
```http
GET /api/chat/rooms/{id}/
```

### List Messages
```http
GET /api/chat/rooms/{chatroom_id}/messages/
```

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "sender": {
        "id": 2,
        "full_name": "John Doe"
      },
      "message": "Hello, I need help with plumbing",
      "attachment": null,
      "is_read": true,
      "created_at": "2026-01-07T10:00:00Z"
    }
  ]
}
```

### Send Message
```http
POST /api/chat/rooms/{chatroom_id}/messages/send/
```

**Request Body:**
```json
{
  "message": "Hello, how can I help you?",
  "attachment": "<file>"
}
```

### Mark Messages as Read
```http
POST /api/chat/rooms/{chatroom_id}/mark-read/
```

### Unread Messages Count
```http
GET /api/chat/unread-count/
```

**Response:**
```json
{
  "unread_count": 5
}
```

---

## Data Models

### User Model
```typescript
interface User {
  id: number;
  email: string;
  phone_number: string;
  full_name: string;
  user_type: 'customer' | 'provider';
  profile_picture?: string;
  date_of_birth?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  is_verified: boolean;
  date_joined: string;
}
```

### Provider Model
```typescript
interface Provider {
  id: number;
  user: User;
  business_name: string;
  bio: string;
  categories: Category[];
  experience_years: number;
  hourly_rate: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  latitude?: string;
  longitude?: string;
  rating: number;
  total_reviews: number;
  total_bookings: number;
  completed_bookings: number;
  completion_rate: number;
  certifications?: string;
  insurance_details?: string;
  website?: string;
  social_media?: object;
  status: 'pending' | 'approved' | 'rejected' | 'suspended';
  profile_picture?: string;
  created_at: string;
  updated_at: string;
}
```

### Service Model
```typescript
interface Service {
  id: number;
  provider: Provider;
  category: Category;
  title: string;
  description: string;
  short_description: string;
  pricing_type: 'hourly' | 'fixed' | 'package';
  base_price: string;
  hourly_rate?: string;
  duration_minutes?: number;
  is_remote: boolean;
  is_onsite: boolean;
  status: 'active' | 'inactive' | 'draft';
  min_booking_hours: number;
  max_bookings_per_day: number;
  image?: string;
  images: ServiceImage[];
  faqs: ServiceFAQ[];
  views_count: number;
  bookings_count: number;
  average_rating: number;
  created_at: string;
  updated_at: string;
}
```

### Booking Model
```typescript
interface Booking {
  id: number;
  customer: User;
  provider: Provider;
  service_title: string;
  service_description: string;
  booking_date: string;
  start_time: string;
  end_time: string;
  duration_hours: string;
  service_address: string;
  city: string;
  postal_code: string;
  hourly_rate: string;
  total_amount: string;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled' | 'refunded';
  customer_notes?: string;
  cancellation_reason?: string;
  created_at: string;
  confirmed_at?: string;
  completed_at?: string;
  cancelled_at?: string;
}
```

### Review Model
```typescript
interface Review {
  id: number;
  customer: User;
  provider: number;
  booking: number;
  rating: number; // 1-5
  comment: string;
  service_quality?: number;
  professionalism?: number;
  value_for_money?: number;
  punctuality?: number;
  images: ReviewImage[];
  response?: ReviewResponse;
  helpful_count: number;
  created_at: string;
  updated_at: string;
}
```

### Payment Model
```typescript
interface Payment {
  id: number;
  booking: Booking;
  amount: string;
  payment_method: 'credit_card' | 'debit_card' | 'paypal' | 'bank_transfer';
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  transaction_id?: string;
  payment_details?: object;
  paid_at?: string;
  created_at: string;
}
```

---

## Frontend Integration Guide

### React/Next.js Example

#### 1. Setup API Client

```javascript
// lib/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${API_BASE_URL}/api/users/token/refresh/`,
          { refresh: refreshToken }
        );
        
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

#### 2. Authentication Hook

```javascript
// hooks/useAuth.js
import { useState, useEffect } from 'react';
import apiClient from '../lib/api';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const response = await apiClient.get('/api/users/profile/');
        setUser(response.data);
      } catch (error) {
        console.error('Auth check failed:', error);
      }
    }
    setLoading(false);
  };

  const login = async (phoneNumber, otp) => {
    try {
      const response = await apiClient.post('/api/users/verify-otp/', {
        phone_number: phoneNumber,
        otp: otp,
      });
      
      const { access, refresh, user } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      setUser(user);
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      await apiClient.post('/api/users/logout/', { refresh: refreshToken });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  return { user, loading, login, logout, checkAuth };
};
```

#### 3. Services API Hook

```javascript
// hooks/useServices.js
import { useState, useEffect } from 'react';
import apiClient from '../lib/api';

export const useServices = (filters = {}) => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchServices();
  }, [JSON.stringify(filters)]);

  const fetchServices = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams(filters);
      const response = await apiClient.get(`/api/services/?${params}`);
      setServices(response.data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { services, loading, error, refetch: fetchServices };
};
```

#### 4. Booking Creation Example

```javascript
// components/BookingForm.jsx
import { useState } from 'react';
import apiClient from '../lib/api';

export const BookingForm = ({ providerId, onSuccess }) => {
  const [formData, setFormData] = useState({
    service_title: '',
    service_description: '',
    booking_date: '',
    start_time: '',
    end_time: '',
    duration_hours: '',
    service_address: '',
    city: '',
    postal_code: '',
    customer_notes: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post('/api/bookings/create/', {
        ...formData,
        provider_id: providerId,
      });
      
      onSuccess(response.data);
    } catch (err) {
      setError(err.response?.data || 'Booking failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <input
        type="text"
        value={formData.service_title}
        onChange={(e) => setFormData({ ...formData, service_title: e.target.value })}
        placeholder="Service Title"
        required
      />
      {/* More fields... */}
      
      {error && <div className="error">{JSON.stringify(error)}</div>}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Booking'}
      </button>
    </form>
  );
};
```

### Vue.js Example

```javascript
// composables/useServices.js
import { ref, watch } from 'vue';
import apiClient from '@/lib/api';

export function useServices(filters = {}) {
  const services = ref([]);
  const loading = ref(true);
  const error = ref(null);

  const fetchServices = async () => {
    try {
      loading.value = true;
      const params = new URLSearchParams(filters);
      const response = await apiClient.get(`/api/services/?${params}`);
      services.value = response.data.results;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  watch(() => filters, fetchServices, { deep: true, immediate: true });

  return { services, loading, error, refetch: fetchServices };
}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "field_errors": {
    "field_name": ["Error message for this field"]
  }
}
```

### Common Error Codes

| Status Code | Meaning | Common Causes |
|------------|---------|---------------|
| 400 | Bad Request | Invalid data, validation errors |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate entry, business rule violation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |

### Error Handling Example

```javascript
try {
  const response = await apiClient.post('/api/bookings/create/', bookingData);
  // Handle success
} catch (error) {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        // Validation errors
        console.error('Validation errors:', data.field_errors);
        break;
      case 401:
        // Unauthorized - redirect to login
        window.location.href = '/login';
        break;
      case 403:
        // Forbidden
        console.error('Access denied:', data.error);
        break;
      case 404:
        // Not found
        console.error('Resource not found');
        break;
      default:
        console.error('Error:', data.error || 'Unknown error');
    }
  } else if (error.request) {
    // No response from server
    console.error('Network error');
  } else {
    // Other errors
    console.error('Error:', error.message);
  }
}
```

---

## Best Practices

### 1. Token Management

```javascript
// Store tokens securely
const storeTokens = (access, refresh) => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
  
  // Set expiration time
  const expiresIn = 5 * 60 * 1000; // 5 minutes
  setTimeout(refreshAccessToken, expiresIn - 30000); // Refresh 30s before expiry
};

const refreshAccessToken = async () => {
  try {
    const refresh = localStorage.getItem('refresh_token');
    const response = await axios.post('/api/users/token/refresh/', { refresh });
    localStorage.setItem('access_token', response.data.access);
  } catch (error) {
    // Handle refresh failure
  }
};
```

### 2. Pagination Handling

```javascript
const fetchAllPages = async (url, params = {}) => {
  let allResults = [];
  let nextUrl = `${url}?${new URLSearchParams(params)}`;
  
  while (nextUrl) {
    const response = await apiClient.get(nextUrl);
    allResults = [...allResults, ...response.data.results];
    nextUrl = response.data.next;
  }
  
  return allResults;
};
```

### 3. File Upload

```javascript
const uploadFile = async (file, endpoint) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('description', 'File description');
  
  const response = await apiClient.post(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};
```

### 4. Caching Strategy

```javascript
// Simple in-memory cache
const cache = new Map();

const getCachedData = async (key, fetcher, ttl = 5 * 60 * 1000) => {
  const cached = cache.get(key);
  
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data;
  }
  
  const data = await fetcher();
  cache.set(key, { data, timestamp: Date.now() });
  
  return data;
};

// Usage
const categories = await getCachedData(
  'service-categories',
  () => apiClient.get('/api/providers/categories/').then(r => r.data)
);
```

### 5. Real-time Updates (WebSocket)

```javascript
// WebSocket connection for chat
const connectWebSocket = (roomId, token) => {
  const ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}/?token=${token}`);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('New message:', data);
    // Update UI
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
    // Reconnect logic
  };
  
  return ws;
};
```

### 6. Search Debouncing

```javascript
import { debounce } from 'lodash';

const searchServices = debounce(async (query) => {
  const response = await apiClient.get(`/api/services/?search=${query}`);
  return response.data.results;
}, 300);
```

---

## Rate Limiting

- **Anonymous users:** 100 requests/hour
- **Authenticated users:** 1000 requests/hour

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641070800
```

---

## API Versioning

Current version: **v1**

Future versions will be available at `/api/v2/...`

---

## Support & Documentation

- **Swagger UI:** http://localhost:8000/swagger/
- **ReDoc:** http://localhost:8000/redoc/
- **Admin Panel:** http://localhost:8000/admin/

---

## Quick Start Checklist

- [ ] Install dependencies and run backend
- [ ] Get API credentials (if needed)
- [ ] Test authentication endpoints
- [ ] Implement token refresh logic
- [ ] Set up error handling
- [ ] Implement caching strategy
- [ ] Test all critical flows
- [ ] Set up real-time features (WebSocket)
- [ ] Implement proper error boundaries
- [ ] Add loading states and skeleton screens

---

**Last Updated:** January 7, 2026  
**Version:** 1.0.0
