# ServiceHub Backend API - Quick Reference for React Frontend

## ⚠️ IMPORTANT: Fix Your Frontend API Calls

**Your Error:** Frontend is calling `/api/api/send-otp/` (double `/api/`)

**Correct Endpoints:**
```
✅ POST http://127.0.0.1:8000/api/users/send-otp/
✅ POST http://127.0.0.1:8000/api/users/verify-otp/
✅ POST http://127.0.0.1:8000/api/users/google-login/
```

---

## Base URL Configuration

```javascript
// src/config/api.js or src/utils/api.js
export const API_BASE_URL = 'http://127.0.0.1:8000';

// DO NOT add /api/ to base URL - it's already in endpoints
export const API_ENDPOINTS = {
  SEND_OTP: '/api/users/send-otp/',
  VERIFY_OTP: '/api/users/verify-otp/',
  GOOGLE_LOGIN: '/api/users/google-login/',
  TOKEN_REFRESH: '/api/users/token/refresh/',
  LOGOUT: '/api/users/logout/',
  PROFILE: '/api/users/profile/',
};
```

---

## 1. Send OTP

```javascript
// ✅ CORRECT
const response = await fetch('http://127.0.0.1:8000/api/users/send-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+1234567890' })
});

// ❌ WRONG - Your current code (double /api/)
const response = await fetch('http://127.0.0.1:8000/api/api/send-otp/', ...);
```

**Request:**
```json
{
  "phone": "+1234567890"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP sent successfully",
  "phone": "+1234567890",
  "otp": "123456",
  "expires_in": "5 minutes"
}
```

---

## 2. Verify OTP & Login/Register

```javascript
const response = await fetch('http://127.0.0.1:8000/api/users/verify-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '+1234567890',
    otp: '123456',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    user_type: 'customer'
  })
});
```

**Request:**
```json
{
  "phone": "+1234567890",
  "otp": "123456",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "user_type": "customer"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP verified successfully",
  "created": true,
  "user": {
    "id": 1,
    "phone": "+1234567890",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "customer",
    "auth_provider": "phone",
    "is_verified": true,
    "full_name": "John Doe"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

## 3. Google Login

```javascript
const response = await fetch('http://127.0.0.1:8000/api/users/google-login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    token: googleCredentialToken,
    user_type: 'customer'
  })
});
```

---

## React Frontend Example

### API Service File
```javascript
// src/services/authService.js
const API_BASE = 'http://127.0.0.1:8000';

export const authService = {
  // Send OTP
  sendOTP: async (phone) => {
    const response = await fetch(`${API_BASE}/api/users/send-otp/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    return response.json();
  },

  // Verify OTP
  verifyOTP: async (data) => {
    const response = await fetch(`${API_BASE}/api/users/verify-otp/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  // Google Login
  googleLogin: async (token, userType = 'customer') => {
    const response = await fetch(`${API_BASE}/api/users/google-login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, user_type: userType })
    });
    return response.json();
  },

  // Get Profile (with token)
  getProfile: async (accessToken) => {
    const response = await fetch(`${API_BASE}/api/users/profile/`, {
      headers: { 
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }
};
```

### Usage in Component
```javascript
// src/components/Login.jsx
import { authService } from '../services/authService';

function Login() {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [showOTPInput, setShowOTPInput] = useState(false);

  const handleSendOTP = async () => {
    try {
      const result = await authService.sendOTP(phone);
      console.log('OTP:', result.otp); // For testing
      setShowOTPInput(true);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleVerifyOTP = async () => {
    try {
      const result = await authService.verifyOTP({
        phone,
        otp,
        user_type: 'customer'
      });
      
      // Save tokens
      localStorage.setItem('access_token', result.tokens.access);
      localStorage.setItem('refresh_token', result.tokens.refresh);
      localStorage.setItem('user', JSON.stringify(result.user));
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <input 
        value={phone} 
        onChange={(e) => setPhone(e.target.value)}
        placeholder="+1234567890"
      />
      <button onClick={handleSendOTP}>Send OTP</button>
      
      {showOTPInput && (
        <>
          <input 
            value={otp} 
            onChange={(e) => setOtp(e.target.value)}
            placeholder="Enter OTP"
          />
          <button onClick={handleVerifyOTP}>Verify</button>
        </>
      )}
    </div>
  );
}
```

---

## All Available Endpoints

```
Authentication:
POST   /api/users/send-otp/         - Send OTP to phone
POST   /api/users/verify-otp/       - Verify OTP & login/register
POST   /api/users/google-login/     - Google OAuth login
POST   /api/users/token/refresh/    - Refresh access token
POST   /api/users/logout/           - Logout (blacklist token)

Profile:
GET    /api/users/profile/          - Get current user profile
PATCH  /api/users/profile/          - Update profile
POST   /api/users/change-password/  - Change password

Admin:
GET    /api/users/                  - List all users (admin)
GET    /api/users/<id>/             - Get user by ID (admin)

Other Apps:
GET    /api/providers/              - List providers
GET    /api/bookings/               - List bookings
GET    /api/payments/               - List payments
GET    /api/reviews/                - List reviews
GET    /api/notifications/          - List notifications
GET    /api/chat/                   - List chat rooms
```

---

## Testing

### Start Backend Server
```bash
cd D:/servicehub
source test/Scripts/activate  # or: test\Scripts\activate.bat on Windows
python manage.py runserver
```

### Test with cURL
```bash
# Send OTP
curl -X POST http://127.0.0.1:8000/api/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'

# Verify OTP
curl -X POST http://127.0.0.1:8000/api/users/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "otp": "123456",
    "first_name": "John",
    "user_type": "customer"
  }'
```

---

## CORS Configuration

Backend allows requests from:
- `http://localhost:3000` (Create React App)
- `http://localhost:5173` (Vite)

If your React app runs on a different port, update `CORS_ALLOWED_ORIGINS` in `settings.py`.

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `404 Not Found: /api/api/send-otp/` | Double `/api/` in URL | Remove extra `/api/` from base URL |
| `CORS Error` | Frontend port not allowed | Add your port to `CORS_ALLOWED_ORIGINS` |
| `401 Unauthorized` | Missing/invalid token | Check `Authorization: Bearer {token}` header |
| `Invalid OTP` | Wrong OTP or expired | Check OTP (valid for 5 minutes) |
