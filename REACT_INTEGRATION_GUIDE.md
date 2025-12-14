# Frontend Integration Guide - ServiceHub Backend

## 🚨 IMPORTANT: Your Current Issues

### Issue 1: Google Client ID Not Found
```
[GSI_LOGGER]: The given client ID is not found.
```

**Fix:** 
1. Get Google OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/)
2. Add to your React `.env` file:
   ```env
   VITE_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   ```
3. Add to backend `.env` file:
   ```env
   GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   ```

### Issue 2: API Endpoint (Fixed on backend)
- ✅ Backend correctly configured at: `http://127.0.0.1:8000/api/users/`
- ⚠️ Your frontend might be calling `/api/api/` (double api)

---

## 📋 Backend API Endpoints

```
Base URL: http://127.0.0.1:8000
```

### Authentication APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/send-otp/` | Send OTP to phone |
| POST | `/api/users/verify-otp/` | Verify OTP & login/register |
| POST | `/api/users/google-login/` | Google OAuth login |
| POST | `/api/users/token/refresh/` | Refresh JWT token |
| POST | `/api/users/logout/` | Logout user |
| GET | `/api/users/profile/` | Get user profile |
| PATCH | `/api/users/profile/` | Update profile |

---

## 🔧 Frontend Setup

### 1. Create API Configuration

```javascript
// src/config/api.js
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  ENDPOINTS: {
    SEND_OTP: '/api/users/send-otp/',
    VERIFY_OTP: '/api/users/verify-otp/',
    GOOGLE_LOGIN: '/api/users/google-login/',
    TOKEN_REFRESH: '/api/users/token/refresh/',
    LOGOUT: '/api/users/logout/',
    PROFILE: '/api/users/profile/',
  }
};
```

### 2. Create Auth Service

```javascript
// src/services/authService.js
import { API_CONFIG } from '../config/api';

const buildURL = (endpoint) => `${API_CONFIG.BASE_URL}${endpoint}`;

export const authService = {
  // Send OTP
  sendOTP: async (phone) => {
    const response = await fetch(buildURL(API_CONFIG.ENDPOINTS.SEND_OTP), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.phone ? error.phone[0] : 'Failed to send OTP');
    }
    
    return response.json();
  },

  // Verify OTP
  verifyOTP: async (phone, otp, userData = {}) => {
    const response = await fetch(buildURL(API_CONFIG.ENDPOINTS.VERIFY_OTP), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phone,
        otp,
        user_type: userData.user_type || 'customer',
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        email: userData.email || ''
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.otp ? error.otp[0] : 'Invalid OTP');
    }
    
    const data = await response.json();
    
    // Save tokens
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  },

  // Google Login
  googleLogin: async (googleToken, userType = 'customer') => {
    const response = await fetch(buildURL(API_CONFIG.ENDPOINTS.GOOGLE_LOGIN), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: googleToken,
        user_type: userType
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Google login failed');
    }
    
    const data = await response.json();
    
    // Save tokens
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  },

  // Get Profile
  getProfile: async () => {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(buildURL(API_CONFIG.ENDPOINTS.PROFILE), {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        // Try to refresh token
        await authService.refreshToken();
        return authService.getProfile();
      }
      throw new Error('Failed to get profile');
    }
    
    return response.json();
  },

  // Refresh Token
  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch(buildURL(API_CONFIG.ENDPOINTS.TOKEN_REFRESH), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (!response.ok) {
      // Refresh token expired, logout
      authService.logout();
      throw new Error('Session expired');
    }
    
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    
    return data;
  },

  // Logout
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
};
```

### 3. Update Login Component

```jsx
// src/pages/auth/Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { authService } from '../../services/authService';

const Login = () => {
  const navigate = useNavigate();
  const [phone, setPhone] = useState('');
  const [otp, setOTP] = useState('');
  const [step, setStep] = useState(1); // 1: phone, 2: otp
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Send OTP
  const handleSendOTP = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await authService.sendOTP(phone);
      console.log('OTP sent:', result.otp); // For development/testing
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Verify OTP
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.verifyOTP(phone, otp, {
        user_type: 'customer' // or get from form
      });
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Google Login
  const handleGoogleSuccess = async (credentialResponse) => {
    setError('');
    setLoading(true);

    try {
      await authService.googleLogin(
        credentialResponse.credential,
        'customer' // or get from form
      );
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {error && <div className="error-message">{error}</div>}

      {/* Phone OTP Login */}
      {step === 1 ? (
        <form onSubmit={handleSendOTP}>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+1234567890"
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Sending...' : 'Send OTP'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOTP}>
          <input
            type="text"
            value={otp}
            onChange={(e) => setOTP(e.target.value)}
            placeholder="Enter OTP"
            maxLength="6"
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Verifying...' : 'Verify & Login'}
          </button>
          <button type="button" onClick={() => setStep(1)}>
            Change Phone Number
          </button>
        </form>
      )}

      {/* Divider */}
      <div className="divider">OR</div>

      {/* Google Login */}
      <GoogleLogin
        onSuccess={handleGoogleSuccess}
        onError={() => setError('Google login failed')}
      />
    </div>
  );
};

export default Login;
```

### 4. Environment Variables

Create `.env` file in your React project root:

```env
# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:8000

# Google OAuth
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### 5. Update App.jsx with Google OAuth Provider

```jsx
// src/App.jsx
import { GoogleOAuthProvider } from '@react-oauth/google';

function App() {
  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
      {/* Your routes */}
    </GoogleOAuthProvider>
  );
}
```

---

## 🧪 Testing

### Test API Calls in Browser Console

Open your React app and run in console:

```javascript
// Test send OTP
fetch('http://127.0.0.1:8000/api/users/send-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+1234567890' })
})
.then(r => r.json())
.then(d => console.log('OTP:', d));

// Test verify OTP
fetch('http://127.0.0.1:8000/api/users/verify-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '+1234567890',
    otp: '123456', // Use OTP from previous call
    user_type: 'customer'
  })
})
.then(r => r.json())
.then(d => console.log('Login:', d));
```

---

## 🔐 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Google+ API"
4. Create OAuth 2.0 credentials
5. Add authorized JavaScript origins:
   - `http://localhost:3000`
   - `http://localhost:3001`
   - `http://localhost:5173`
6. Add authorized redirect URIs:
   - `http://localhost:3000`
   - `http://localhost:3001`
   - `http://localhost:5173`
7. Copy Client ID and add to both:
   - React `.env`: `VITE_GOOGLE_CLIENT_ID=...`
   - Backend `.env`: `GOOGLE_OAUTH_CLIENT_ID=...`

---

## 📝 API Request/Response Examples

### Send OTP
**Request:**
```json
POST /api/users/send-otp/
{
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully",
  "phone": "+1234567890",
  "otp": "123456",
  "expires_in": "5 minutes"
}
```

### Verify OTP
**Request:**
```json
POST /api/users/verify-otp/
{
  "phone": "+1234567890",
  "otp": "123456",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "user_type": "customer"
}
```

**Response:**
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
    "is_verified": true
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJh...",
    "access": "eyJ0eXAiOiJKV1QiLCJh..."
  }
}
```

---

## ⚠️ Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `404 Not Found: /api/api/send-otp/` | Double `/api/` in URL | Check API base URL config |
| `CORS Error` | Frontend port not allowed | Add port to backend CORS settings |
| `401 Unauthorized` | Invalid/expired token | Implement token refresh |
| `Invalid OTP` | Wrong OTP or expired | OTP valid for 5 minutes only |
| `Google Client ID not found` | Missing/wrong Client ID | Set correct ID in `.env` files |

---

## 🔄 Token Refresh Implementation

```javascript
// src/utils/api.js
export const fetchWithAuth = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.status === 401) {
    // Token expired, refresh it
    const refreshToken = localStorage.getItem('refresh_token');
    
    const refreshResponse = await fetch('http://127.0.0.1:8000/api/users/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      localStorage.setItem('access_token', data.access);
      
      // Retry original request
      return fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${data.access}`,
          'Content-Type': 'application/json'
        }
      });
    } else {
      // Refresh failed, logout
      localStorage.clear();
      window.location.href = '/login';
    }
  }
  
  return response;
};
```

---

## 📦 Required NPM Packages

```bash
npm install @react-oauth/google
```

---

## ✅ Checklist

- [ ] Backend server running at `http://127.0.0.1:8000`
- [ ] Google OAuth Client ID configured
- [ ] API base URL set to `http://127.0.0.1:8000` (no trailing `/api/`)
- [ ] Auth service created with all API calls
- [ ] Token storage implemented
- [ ] Error handling added
- [ ] Token refresh logic implemented
- [ ] Google OAuth provider wrapped around app
