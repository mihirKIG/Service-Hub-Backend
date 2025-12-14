# 🔴 FRONTEND FIX REQUIRED

## Your Error
```
Not Found: /api/api/send-otp/
[04/Dec/2025 12:26:01] "POST /api/api/send-otp/ HTTP/1.1" 404 4015
```

## Problem
Your React frontend is calling `/api/api/send-otp/` with **double `/api/`**

## Solution
Update your frontend API base URL configuration:

### ❌ WRONG Configuration
```javascript
// DON'T DO THIS
const API_BASE_URL = 'http://127.0.0.1:8000/api';
const endpoint = '/api/send-otp/';  // This creates /api/api/send-otp/
```

### ✅ CORRECT Configuration (Option 1)
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';
const endpoint = '/api/users/send-otp/';
const fullURL = `${API_BASE_URL}${endpoint}`;
// Result: http://127.0.0.1:8000/api/users/send-otp/ ✅
```

### ✅ CORRECT Configuration (Option 2)
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/users';
const endpoint = '/send-otp/';
const fullURL = `${API_BASE_URL}${endpoint}`;
// Result: http://127.0.0.1:8000/api/users/send-otp/ ✅
```

## Complete Endpoint List

```javascript
// Backend URL structure
const ENDPOINTS = {
  // Authentication
  SEND_OTP: 'http://127.0.0.1:8000/api/users/send-otp/',
  VERIFY_OTP: 'http://127.0.0.1:8000/api/users/verify-otp/',
  GOOGLE_LOGIN: 'http://127.0.0.1:8000/api/users/google-login/',
  
  // Token Management
  TOKEN_REFRESH: 'http://127.0.0.1:8000/api/users/token/refresh/',
  LOGOUT: 'http://127.0.0.1:8000/api/users/logout/',
  
  // Profile
  PROFILE: 'http://127.0.0.1:8000/api/users/profile/',
  CHANGE_PASSWORD: 'http://127.0.0.1:8000/api/users/change-password/',
};
```

## Quick Test in Browser Console

Open your React app's browser console and run:

```javascript
// Test send OTP
fetch('http://127.0.0.1:8000/api/users/send-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+1234567890' })
})
.then(res => res.json())
.then(data => console.log('OTP:', data.otp));
```

## Recommended Frontend Structure

```javascript
// src/config/api.js
export const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000',
  ENDPOINTS: {
    AUTH: {
      SEND_OTP: '/api/users/send-otp/',
      VERIFY_OTP: '/api/users/verify-otp/',
      GOOGLE_LOGIN: '/api/users/google-login/',
      TOKEN_REFRESH: '/api/users/token/refresh/',
      LOGOUT: '/api/users/logout/',
    },
    PROFILE: {
      GET: '/api/users/profile/',
      UPDATE: '/api/users/profile/',
      CHANGE_PASSWORD: '/api/users/change-password/',
    }
  }
};

// Helper function
export const buildURL = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Usage
import { API_CONFIG, buildURL } from './config/api';

const url = buildURL(API_CONFIG.ENDPOINTS.AUTH.SEND_OTP);
// Result: http://127.0.0.1:8000/api/users/send-otp/
```

## Working Example

```javascript
// src/services/authService.js
const API_BASE = 'http://127.0.0.1:8000';

export const sendOTP = async (phone) => {
  const response = await fetch(`${API_BASE}/api/users/send-otp/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
};

export const verifyOTP = async (phone, otp, userData = {}) => {
  const response = await fetch(`${API_BASE}/api/users/verify-otp/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone, otp, ...userData })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
};
```

## Check Your Files

Look for these patterns in your React code:

1. **API configuration file** (usually `src/config/api.js` or `src/utils/api.js`)
2. **Auth service** (usually `src/services/authService.js`)
3. **Component files** that make API calls

Search for:
- `"/api/api/"` (double api)
- `"api/api/"` (double api)
- Base URL ending with `/api`

## After Fix

Once fixed, you should see:
```
[04/Dec/2025 12:26:01] "POST /api/users/send-otp/ HTTP/1.1" 200 120
```

Instead of:
```
Not Found: /api/api/send-otp/
[04/Dec/2025 12:26:01] "POST /api/api/send-otp/ HTTP/1.1" 404 4015
```
