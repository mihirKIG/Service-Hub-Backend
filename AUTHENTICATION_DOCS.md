# ServiceHub Authentication System Documentation

## Overview
ServiceHub uses a modern, secure authentication system with **ONLY** two methods:
1. **Phone OTP Authentication** - Temporary 6-digit code verification (2-minute expiry)
2. **Google Sign-In** - OAuth2 authentication via Google ID Token

**REMOVED:** Email/Username/Password authentication has been completely removed from the system.

---

## Authentication Architecture

### User Model Structure
```python
# users/models.py
class User(AbstractBaseUser, PermissionsMixin):
    # Primary Fields
    phone = CharField(unique=True, max_length=20)  # USERNAME_FIELD
    google_uid = CharField(unique=True, nullable=True)  # For Google auth
    is_verified = BooleanField(default=False)
    
    # Optional Profile Fields
    first_name = CharField(blank=True)
    last_name = CharField(blank=True)
    email = EmailField(nullable=True, blank=True)
    profile_picture = URLField(nullable=True, blank=True)
    
    # System Fields
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    date_joined = DateTimeField(auto_now_add=True)
    last_login = DateTimeField(nullable=True)
```

**Key Design Decisions:**
- `phone` is the `USERNAME_FIELD` (primary identifier)
- No `username` field
- No `password` field
- `google_uid` for Google-authenticated users
- `email` is optional (collected from Google or manually)

###OTP Storage
- **Development:** In-memory cache (`django.core.cache.backends.locmem.LocMemCache`)
- **Production:** Redis cache (`django_redis.cache.RedisCache`)
- **TTL:** 120 seconds (2 minutes)
- **Cache Key Format:** `otp_{phone_number}`

---

## API Endpoints

### Base URL
```
http://127.0.0.1:8000/api/users/
```

### 1. Send OTP
**Endpoint:** `POST /api/users/send-otp/`

**Purpose:** Generate and send a 6-digit OTP to the user's phone number.

**Request Body:**
```json
{
  "phone": "+919876543210"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "phone": "+919876543210",
  "otp": "739452",  // Only in DEBUG mode for testing
  "expires_in_seconds": 120
}
```

**Validation:**
- Phone must match E.164 format: `+[1-9][0-9]{1,14}`
- Generates random 6-digit code
- Stores in cache with 2-minute expiry
- In production, OTP would be sent via SMS (Twilio)

---

### 2. Verify OTP & Login
**Endpoint:** `POST /api/users/verify-otp/`

**Purpose:** Verify OTP and automatically login/register the user.

**Request Body:**
```json
{
  "phone": "+919876543210",
  "otp": "739452"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "user": {
    "id": 1,
    "phone": "+919876543210",
    "email": null,
    "first_name": "",
    "last_name": "",
    "is_verified": true,
    "profile_picture": null
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",  // JWT Access Token (1 hour)
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",  // JWT Refresh Token (7 days)
  "is_new_user": true
}
```

**Response (Error - 400):**
```json
{
  "error": "Invalid or expired OTP"
}
```

**Flow:**
1. Retrieves OTP from cache using phone number
2. Validates OTP matches user input
3. Deletes OTP from cache (single-use)
4. Creates user if doesn't exist (`is_new_user: true`)
5. Marks user as verified
6. Generates JWT access & refresh tokens
7. Returns user data and tokens

---

### 3. Google Sign-In
**Endpoint:** `POST /api/users/google/`

**Purpose:** Authenticate user via Google ID Token.

**Request Body:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI..."  // From Google Sign-In
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Google authentication successful",
  "user": {
    "id": 2,
    "phone": "",  // Optional - can be added later
    "email": "user@gmail.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": true,
    "profile_picture": "https://lh3.googleusercontent.com/..."
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "is_new_user": false
}
```

**Response (Error - 400):**
```json
{
  "error": "Invalid Google ID token"
}
```

**Flow:**
1. Verifies Google ID Token using `google.oauth2.id_token.verify_oauth2_token()`
2. Extracts user info: `sub` (google_uid), `email`, `name`, `picture`
3. Checks if user exists with `google_uid`
4. Creates new user if first-time Google login
5. Updates profile info from Google data
6. Marks user as verified
7. Generates JWT tokens
8. Returns user data and tokens

**Getting Google ID Token:**
- Frontend must integrate Google Sign-In SDK
- Use `@react-oauth/google` or `gapi.auth2`
- ID Token is obtained from Google OAuth flow
- Pass token directly to this endpoint

---

### 4. Get User Profile
**Endpoint:** `GET /api/users/profile/`

**Purpose:** Retrieve authenticated user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (Success - 200):**
```json
{
  "id": 1,
  "phone": "+919876543210",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_verified": true,
  "profile_picture": "https://example.com/pic.jpg"
}
```

**Response (Error - 401):**
```json
{
  "detail": "Given token not valid for any token type"
}
```

---

### 5. Update User Profile
**Endpoint:** `PATCH /api/users/profile/`

**Purpose:** Update user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (all fields optional):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "profile_picture": "https://example.com/new-pic.jpg"
}
```

**Response (Success - 200):**
```json
{
  "id": 1,
  "phone": "+919876543210",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_verified": true,
  "profile_picture": "https://example.com/new-pic.jpg"
}
```

**Note:** `phone` and `google_uid` cannot be updated.

---

### 6. Refresh JWT Token
**Endpoint:** `POST /api/users/token/refresh/`

**Purpose:** Get new access token using refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (Success - 200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (Error - 401):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 7. Logout
**Endpoint:** `POST /api/users/logout/`

**Purpose:** Blacklist refresh token to prevent reuse.

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

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

**Response (Error - 400):**
```json
{
  "error": "Refresh token is required"
}
```

---

## JWT Configuration

### Token Lifetimes
- **Access Token:** 1 hour
- **Refresh Token:** 7 days
- **Algorithm:** HS256
- **Auto Blacklist:** Refresh tokens are blacklisted after rotation
- **Update Last Login:** Yes

### Token Usage
```javascript
// Example: Making authenticated requests
const accessToken = "eyJ0eXAiOiJKV1QiLCJhbGc...";

fetch('http://127.0.0.1:8000/api/users/profile/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

### Token Refresh Flow
1. Store both `access` and `refresh` tokens after login
2. Use `access` token for all API requests
3. When access token expires (401 error), use refresh token:
   ```javascript
   POST /api/users/token/refresh/
   Body: { "refresh": "<refresh_token>" }
   ```
4. Get new `access` token
5. Retry original request with new token
6. If refresh token expires, user must login again

---

## Error Responses

### Common HTTP Status Codes
- **200 OK** - Successful request
- **400 Bad Request** - Invalid input data
- **401 Unauthorized** - Missing or invalid authentication token
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

### Error Response Format
```json
{
  "error": "Detailed error message"
}
```

---

## Frontend Integration Guide

### 1. Phone OTP Flow

#### Step 1: Send OTP
```javascript
async function sendOTP(phone) {
  const response = await fetch('http://127.0.0.1:8000/api/users/send-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone })
  });
  
  const data = await response.json();
  if (response.ok) {
    console.log('OTP sent:', data.otp);  // Only in dev mode
    return data;
  } else {
    throw new Error(data.error);
  }
}

// Usage
sendOTP('+919876543210');
```

#### Step 2: Verify OTP
```javascript
async function verifyOTP(phone, otp) {
  const response = await fetch('http://127.0.0.1:8000/api/users/verify-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, otp })
  });
  
  const data = await response.json();
  if (response.ok) {
    // Store tokens in localStorage or secure storage
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('refreshToken', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  } else {
    throw new Error(data.error);
  }
}

// Usage
verifyOTP('+919876543210', '123456');
```

### 2. Google Sign-In Flow

#### Install Package
```bash
npm install @react-oauth/google
```

#### Setup Google OAuth
```javascript
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

function App() {
  return (
    <GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
      <GoogleAuth />
    </GoogleOAuthProvider>
  );
}

function GoogleAuth() {
  const handleGoogleSuccess = async (credentialResponse) => {
    const idToken = credentialResponse.credential;
    
    const response = await fetch('http://127.0.0.1:8000/api/users/google/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: idToken })
    });
    
    const data = await response.json();
    if (response.ok) {
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } else {
      console.error('Google auth failed:', data.error);
    }
  };
  
  return (
    <GoogleLogin
      onSuccess={handleGoogleSuccess}
      onError={() => console.log('Login Failed')}
    />
  );
}
```

### 3. Authenticated Requests

#### API Client with Auto Token Refresh
```javascript
class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }
  
  async request(endpoint, options = {}) {
    let accessToken = localStorage.getItem('accessToken');
    
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    };
    
    let response = await fetch(`${this.baseURL}${endpoint}`, options);
    
    // If token expired, refresh and retry
    if (response.status === 401) {
      const refreshToken = localStorage.getItem('refreshToken');
      const refreshResponse = await fetch(`${this.baseURL}/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      });
      
      if (refreshResponse.ok) {
        const data = await refreshResponse.json();
        localStorage.setItem('accessToken', data.access);
        
        // Retry original request
        options.headers.Authorization = `Bearer ${data.access}`;
        response = await fetch(`${this.baseURL}${endpoint}`, options);
      } else {
        // Refresh failed, logout user
        this.logout();
        window.location.href = '/login';
      }
    }
    
    return response.json();
  }
  
  logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }
}

// Usage
const api = new APIClient('http://127.0.0.1:8000/api/users');
const profile = await api.request('/profile/', { method: 'GET' });
```

---

## Security Features

### 1. OTP Security
- **Single Use:** OTP deleted from cache after verification
- **Time-Limited:** 2-minute expiry (120 seconds)
- **Random Generation:** 6-digit cryptographically secure random number
- **Rate Limiting:** (TODO) Implement rate limiting for OTP generation

### 2. JWT Security
- **Token Blacklisting:** Refresh tokens blacklisted on logout
- **Token Rotation:** New refresh token generated on each refresh
- **Short-Lived Access Tokens:** 1-hour lifetime reduces exposure
- **HTTP-Only Cookies:** (TODO) Consider storing tokens in HTTP-only cookies

### 3. Google OAuth Security
- **Token Verification:** ID token verified using Google's public keys
- **Audience Check:** Ensures token intended for your app
- **Issuer Validation:** Confirms token issued by Google
- **Expiry Check:** Rejects expired tokens

### 4. Django Security
- **CSRF Protection:** Enabled for state-changing requests
- **CORS:** Configured for specific frontend origins
- **Password Hashing:** (Not used, but available for superuser)
- **SQL Injection Protection:** Django ORM prevents SQL injection

---

## Environment Configuration

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/servicehub

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Redis (Production)
REDIS_HOST=127.0.0.1

# SMS (Future - Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Django
SECRET_KEY=your-secret-key
DEBUG=True
```

### Cache Configuration (Development vs Production)
```python
# Development (In-Memory)
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'otp-cache',
            'TIMEOUT': 120,
        }
    }

# Production (Redis)
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:6379/1",
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'TIMEOUT': 120,
        }
    }
```

---

## Testing

### Manual Testing with cURL

#### 1. Send OTP
```bash
curl -X POST http://127.0.0.1:8000/api/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919876543210"}'
```

#### 2. Verify OTP
```bash
curl -X POST http://127.0.0.1:8000/api/users/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919876543210","otp":"123456"}'
```

#### 3. Get Profile
```bash
curl -X GET http://127.0.0.1:8000/api/users/profile/ \
  -H "Authorization: Bearer <access_token>"
```

#### 4. Update Profile
```bash
curl -X PATCH http://127.0.0.1:8000/api/users/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe"}'
```

#### 5. Logout
```bash
curl -X POST http://127.0.0.1:8000/api/users/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

### Automated Testing
See `test_auth_endpoints.py` for comprehensive endpoint testing.

```bash
python test_auth_endpoints.py
```

---

## Migration from Old System

### Changes Made
1. **Removed Fields:**
   - `username` (was USERNAME_FIELD)
   - `password` (no password authentication)
   - `user_type` (customer/provider/admin)
   - `auth_provider` (phone/google flag)
   - `address` (moved to profile extension)

2. **Added Fields:**
   - `google_uid` (unique identifier for Google users)
   - `phone` as new USERNAME_FIELD

3. **Removed Models:**
   - `OTP` model (now uses cache)

4. **Removed Views:**
   - `UserRegistrationView`
   - `UserLoginView`
   - `ChangePasswordView`
   - Admin user management views

5. **Added Views:**
   - `SendOTPView`
   - `VerifyOTPView`
   - `GoogleAuthView`

### Database Migration
```bash
# 1. Backup old database
pg_dump servicehub > backup.sql

# 2. Delete old migrations
rm users/migrations/0001_initial.py

# 3. Create fresh migrations
python manage.py makemigrations users

# 4. Apply migrations
python manage.py migrate

# 5. Create superuser (phone-based)
python manage.py createsuperuser
# Phone: +911234567890
```

---

## Future Enhancements

### 1. SMS Integration (Twilio)
```python
# users/serializers.py - SendOTPSerializer.save()
from twilio.rest import Client

def send_sms_otp(phone, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f'Your ServiceHub OTP is: {otp}. Valid for 2 minutes.',
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone
    )
    return message.sid
```

### 2. Rate Limiting
```python
# users/views.py
from rest_framework.throttling import AnonRateThrottle

class OTPRateThrottle(AnonRateThrottle):
    rate = '5/hour'  # 5 OTP requests per hour per IP

class SendOTPView(APIView):
    throttle_classes = [OTPRateThrottle]
```

### 3. Phone Number Verification
- Add `is_phone_verified` field
- Require phone verification before certain actions
- Send verification SMS after registration

### 4. Multi-Factor Authentication (MFA)
- Optional TOTP (Time-based One-Time Password)
- Backup codes for account recovery
- Email verification as second factor

### 5. Social Auth Extension
- Facebook Login
- Apple Sign-In
- LinkedIn OAuth

---

## Troubleshooting

### Common Issues

#### 1. OTP Not Found/Expired
**Problem:** "Invalid or expired OTP"
**Causes:**
- OTP expired (>2 minutes old)
- OTP already used (single-use)
- Cache cleared/restarted
- Wrong phone number

**Solution:**
- Generate new OTP
- Ensure verification within 2 minutes
- Check cache backend is running

#### 2. Google Token Invalid
**Problem:** "Invalid Google ID token"
**Causes:**
- Expired token (1-hour lifetime)
- Wrong CLIENT_ID in backend
- Token from different Google app
- Network issues during verification

**Solution:**
- Ensure `GOOGLE_OAUTH_CLIENT_ID` matches frontend
- Re-login with Google to get fresh token
- Check Google Cloud Console credentials

#### 3. JWT Token Expired
**Problem:** 401 Unauthorized
**Causes:**
- Access token expired (>1 hour old)
- Refresh token expired (>7 days old)
- Token blacklisted (after logout)

**Solution:**
- Use refresh token to get new access token
- If refresh fails, user must login again

#### 4. Phone Format Invalid
**Problem:** Validation error on phone field
**Cause:** Phone not in E.164 format

**Solution:**
```javascript
// Correct format
+919876543210  ✅
+1234567890    ✅

// Incorrect format
9876543210     ❌
+91 98765 43210 ❌
```

---

## API Testing with Postman

### Collection Structure
```
ServiceHub Auth API
├── 1. Send OTP
│   └── POST /api/users/send-otp/
├── 2. Verify OTP
│   └── POST /api/users/verify-otp/
├── 3. Google Sign-In
│   └── POST /api/users/google/
├── 4. Get Profile
│   └── GET /api/users/profile/
├── 5. Update Profile
│   └── PATCH /api/users/profile/
├── 6. Refresh Token
│   └── POST /api/users/token/refresh/
└── 7. Logout
    └── POST /api/users/logout/
```

### Environment Variables
```
base_url = http://127.0.0.1:8000
access_token = {{access_token}}
refresh_token = {{refresh_token}}
```

### Pre-request Script (Auto Token)
```javascript
// For authenticated endpoints
const accessToken = pm.environment.get("access_token");
pm.request.headers.add({
    key: 'Authorization',
    value: `Bearer ${accessToken}`
});
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Set `DEBUG = False` in production
- [ ] Configure Redis for cache backend
- [ ] Setup Twilio for SMS OTP delivery
- [ ] Add proper CORS allowed origins
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set strong `SECRET_KEY`
- [ ] Configure environment variables
- [ ] Setup database backups
- [ ] Enable logging and monitoring

### Post-Deployment
- [ ] Test all authentication endpoints
- [ ] Verify OTP delivery via SMS
- [ ] Test Google Sign-In with production credentials
- [ ] Monitor error logs
- [ ] Setup alerts for failed auth attempts
- [ ] Document API for frontend team
- [ ] Perform security audit
- [ ] Load testing for OTP generation

---

## Support & Maintenance

### Logs Location
```bash
# Django logs
tail -f logs/django.log

# nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Database Queries
```sql
-- Check user count
SELECT COUNT(*) FROM users;

-- Find users by auth method
SELECT COUNT(*), 
  CASE 
    WHEN google_uid IS NOT NULL THEN 'Google'
    ELSE 'Phone OTP'
  END as auth_method
FROM users
GROUP BY auth_method;

-- Check verified users
SELECT COUNT(*) FROM users WHERE is_verified = TRUE;
```

### Cache Monitoring
```bash
# Redis CLI
redis-cli

# List OTP keys
KEYS otp_*

# Check OTP for phone
GET otp_+919876543210

# Check TTL
TTL otp_+919876543210
```

---

## Contact

For questions or issues:
- **Backend Team:** backend@servicehub.com
- **Documentation:** https://docs.servicehub.com
- **GitHub:** https://github.com/servicehub/backend

---

**Last Updated:** December 4, 2025
**Version:** 2.0.0
**Django:** 5.0
**DRF:** 3.14.0
