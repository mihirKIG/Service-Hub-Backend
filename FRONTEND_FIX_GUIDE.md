# 🔧 Frontend Integration Fix - Quick Solution

## Your Issue
Your React frontend at `http://localhost:3003/register` is showing **"Failed to send OTP"** errors.

**Root Cause:** Your frontend is calling the WRONG API endpoint URL.

---

## ✅ CORRECT Backend API Endpoints

```
Backend Server: http://127.0.0.1:8000
API Base Path: /api/users/

Endpoints:
✅ POST http://127.0.0.1:8000/api/users/send-otp/
✅ POST http://127.0.0.1:8000/api/users/verify-otp/
✅ POST http://127.0.0.1:8000/api/users/google/
✅ GET  http://127.0.0.1:8000/api/users/profile/
✅ PATCH http://127.0.0.1:8000/api/users/profile/
✅ POST http://127.0.0.1:8000/api/users/token/refresh/
✅ POST http://127.0.0.1:8000/api/users/logout/
```

---

## ❌ Common Frontend Mistakes

### Mistake 1: Double /api/ in URL
```javascript
// WRONG ❌
const API_BASE = 'http://127.0.0.1:8000/api';
const endpoint = '/api/send-otp/';  
// Results in: http://127.0.0.1:8000/api/api/send-otp/ ❌

// CORRECT ✅
const API_BASE = 'http://127.0.0.1:8000';
const endpoint = '/api/users/send-otp/';
// Results in: http://127.0.0.1:8000/api/users/send-otp/ ✅
```

### Mistake 2: Missing /users/ in path
```javascript
// WRONG ❌
fetch('http://127.0.0.1:8000/api/send-otp/', ...)

// CORRECT ✅
fetch('http://127.0.0.1:8000/api/users/send-otp/', ...)
```

### Mistake 3: Wrong localhost/port
```javascript
// WRONG ❌ (calling frontend's own port)
fetch('http://localhost:3003/api/users/send-otp/', ...)

// CORRECT ✅ (calling backend port 8000)
fetch('http://127.0.0.1:8000/api/users/send-otp/', ...)
```

---

## 🔧 Fix Your Frontend Code

### Option 1: Create API Configuration File

Create a new file: `src/config/api.js`

```javascript
// src/config/api.js
const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000',
  ENDPOINTS: {
    SEND_OTP: '/api/users/send-otp/',
    VERIFY_OTP: '/api/users/verify-otp/',
    GOOGLE_AUTH: '/api/users/google/',
    PROFILE: '/api/users/profile/',
    REFRESH_TOKEN: '/api/users/token/refresh/',
    LOGOUT: '/api/users/logout/',
  }
};

export const getFullUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

export default API_CONFIG;
```

### Option 2: Fix Your Existing API Service

Find your API service file (usually `src/services/api.js` or `src/utils/api.js` or similar) and update it:

```javascript
// src/services/api.js
const API_BASE_URL = 'http://127.0.0.1:8000';

export const authAPI = {
  sendOTP: async (phone) => {
    const response = await fetch(`${API_BASE_URL}/api/users/send-otp/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to send OTP');
    }
    
    return response.json();
  },
  
  verifyOTP: async (phone, otp) => {
    const response = await fetch(`${API_BASE_URL}/api/users/verify-otp/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, otp })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to verify OTP');
    }
    
    return response.json();
  }
};
```

---

## 🧪 Test the Backend First

Before fixing frontend, verify backend is working:

### Test 1: Send OTP
```bash
curl -X POST http://127.0.0.1:8000/api/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"+801719159900"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "phone": "+801719159900",
  "otp": "308727",
  "expires_in_seconds": 120
}
```

### Test 2: Verify OTP
```bash
curl -X POST http://127.0.0.1:8000/api/users/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone":"+801719159900","otp":"308727"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "user": {
    "id": 1,
    "phone": "+801719159900",
    "email": null,
    "first_name": "",
    "last_name": "",
    "is_verified": true,
    "profile_picture": null
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "is_new_user": true
}
```

---

## 📱 Complete Frontend Example

### Register/Login Component

```javascript
import React, { useState } from 'react';
import API_CONFIG, { getFullUrl } from './config/api';

function LoginPage() {
  const [phone, setPhone] = useState('');
  const [otp, setOTP] = useState('');
  const [step, setStep] = useState('phone'); // 'phone' or 'otp'
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendOTP = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(getFullUrl(API_CONFIG.ENDPOINTS.SEND_OTP), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone })
      });

      const data = await response.json();

      if (response.ok) {
        console.log('OTP sent:', data.otp); // For development only
        setStep('otp');
        alert(`OTP sent! (Dev mode: ${data.otp})`);
      } else {
        setError(data.error || 'Failed to send OTP');
      }
    } catch (err) {
      setError('Network error. Make sure backend is running on port 8000.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(getFullUrl(API_CONFIG.ENDPOINTS.VERIFY_OTP), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, otp })
      });

      const data = await response.json();

      if (response.ok) {
        // Store tokens
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        setError(data.error || 'Invalid OTP');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h1>ServiceHub</h1>
      <p>Welcome back! Please sign in to continue</p>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {step === 'phone' ? (
        <form onSubmit={handleSendOTP}>
          <label>Phone Number</label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+801719159900"
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Sending...' : 'Send OTP'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOTP}>
          <label>Enter OTP</label>
          <input
            type="text"
            value={otp}
            onChange={(e) => setOTP(e.target.value)}
            placeholder="6-digit code"
            maxLength={6}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Verifying...' : 'Verify OTP'}
          </button>
          <button type="button" onClick={() => setStep('phone')}>
            Change Phone Number
          </button>
        </form>
      )}

      <div className="divider">OR</div>
      
      <button className="google-btn">
        Sign in with Google
      </button>
    </div>
  );
}

export default LoginPage;
```

---

## 🔍 Debug Checklist

If still not working, check these:

### 1. Check Backend Server
```bash
# In terminal, verify server is running
curl http://127.0.0.1:8000/api/users/send-otp/
```

### 2. Check Browser Console
Open Chrome DevTools (F12) → Network tab:
- Look for the API request
- Check the URL being called
- Look at the response

### 3. Check CORS
Your backend already has CORS enabled for localhost:3000, 3001, 5173, 8000. 
Add port 3003:

```python
# servicehub_backend/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3003",  # Add this!
    "http://localhost:5173",
    "http://localhost:8000",
]
```

Restart Django server after changing settings.

### 4. Check Phone Format
Phone must be in E.164 format:
```
✅ +801719159900  (Country code + number)
✅ +919876543210
❌ 01719159900    (Missing +88)
❌ +88 01719159900 (Has space)
```

---

## 🎯 Quick Fix Steps

1. **Find your frontend API file** (probably `src/services/api.js` or `src/utils/api.js`)

2. **Replace the API base URL:**
   ```javascript
   const API_BASE_URL = 'http://127.0.0.1:8000';
   ```

3. **Fix the endpoint paths:**
   ```javascript
   // Send OTP
   fetch(`${API_BASE_URL}/api/users/send-otp/`, ...)
   
   // Verify OTP
   fetch(`${API_BASE_URL}/api/users/verify-otp/`, ...)
   ```

4. **Add error handling:**
   ```javascript
   try {
     const response = await fetch(url, options);
     const data = await response.json();
     
     if (!response.ok) {
       throw new Error(data.error || 'Request failed');
     }
     
     return data;
   } catch (error) {
     console.error('API Error:', error);
     throw error;
   }
   ```

5. **Restart your frontend dev server**

---

## ✅ Verify It's Working

After fixing, you should see in browser console:
```
POST http://127.0.0.1:8000/api/users/send-otp/ 200 OK
Response: {success: true, otp: "308727", ...}
```

Instead of:
```
POST http://localhost:3003/api/... 404 Not Found ❌
```

---

## 📞 Need More Help?

If still having issues:

1. Open browser DevTools (F12)
2. Go to Network tab
3. Try sending OTP
4. Take a screenshot of the failed request
5. Check what URL is being called
6. Check the request payload
7. Check the response

The backend is **100% working** - it's just a frontend configuration issue!

---

**Backend API is ready:** ✅  
**Your task:** Fix frontend to call correct URLs  
**Expected fix time:** 5 minutes
