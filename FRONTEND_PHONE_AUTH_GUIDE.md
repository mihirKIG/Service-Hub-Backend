# Frontend Integration Guide - Phone OTP Authentication

## 🎯 Complete Authentication Flow

Your backend is now configured with **BulkSMS BD** for sending real OTP messages to Bangladesh phone numbers.

---

## 📱 Step 1: Send OTP

### Endpoint
```
POST http://127.0.0.1:8000/api/users/send-otp/
```

### Request Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "phone": "+8801719159900"
}
```

**Phone Format:** 
- With country code: `+8801719159900` or `8801719159900`
- Without country code: `01719159900`

### Response (Success)
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "phone": "+8801719159900",
  "otp": "123456",
  "expires_in_seconds": 120
}
```

**Note:** `otp` field is only visible in DEBUG mode. In production (DEBUG=False), it won't be returned.

### Response (Error)
```json
{
  "phone": ["Enter a valid phone number with country code (E.164 format)"]
}
```

### Frontend Code Example (React/JavaScript)
```javascript
async function sendOTP(phoneNumber) {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/users/send-otp/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: phoneNumber  // e.g., "+8801719159900"
      })
    });

    const data = await response.json();
    
    if (data.success) {
      console.log('OTP sent successfully');
      console.log('OTP (dev only):', data.otp);  // Only in DEBUG mode
      return { success: true, data };
    } else {
      console.error('Error:', data);
      return { success: false, error: data };
    }
  } catch (error) {
    console.error('Network error:', error);
    return { success: false, error };
  }
}

// Usage
sendOTP('+8801719159900');
```

---

## ✅ Step 2: Verify OTP

### Endpoint
```
POST http://127.0.0.1:8000/api/users/verify-otp/
```

### Request Headers
```
Content-Type: application/json
```

### Request Body (Minimum)
```json
{
  "phone": "+8801719159900",
  "otp": "123456"
}
```

### Request Body (With Optional Profile Info)
```json
{
  "phone": "+8801719159900",
  "otp": "123456",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com"
}
```

### Response (Success - New User)
```json
{
  "success": true,
  "message": "Registration successful",
  "created": true,
  "user": {
    "id": 1,
    "phone": "+8801719159900",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "is_verified": true,
    "profile_picture": null,
    "date_joined": "2025-12-09T14:30:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Response (Success - Existing User)
```json
{
  "success": true,
  "message": "Login successful",
  "created": false,
  "user": {
    "id": 1,
    "phone": "+8801719159900",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "is_verified": true,
    "profile_picture": null,
    "date_joined": "2025-12-09T14:30:00Z"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Response (Error - Invalid OTP)
```json
{
  "otp": ["Invalid or expired OTP"]
}
```

### Frontend Code Example (React/JavaScript)
```javascript
async function verifyOTP(phoneNumber, otp, profileData = {}) {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/users/verify-otp/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: phoneNumber,
        otp: otp,
        ...profileData  // Optional: first_name, last_name, email
      })
    });

    const data = await response.json();
    
    if (data.success) {
      // Store tokens in localStorage or secure storage
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      console.log('Authentication successful');
      return { success: true, data };
    } else {
      console.error('Verification failed:', data);
      return { success: false, error: data };
    }
  } catch (error) {
    console.error('Network error:', error);
    return { success: false, error };
  }
}

// Usage
verifyOTP('+8801719159900', '123456', {
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com'
});
```

---

## 🔐 Step 3: Use JWT Token for Protected Routes

After successful login, use the access token for authenticated requests:

### Example: Get User Profile

#### Endpoint
```
GET http://127.0.0.1:8000/api/users/profile/
```

#### Request Headers
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

#### Response
```json
{
  "id": 1,
  "phone": "+8801719159900",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "is_verified": true,
  "profile_picture": null,
  "date_joined": "2025-12-09T14:30:00Z"
}
```

### Frontend Code Example
```javascript
async function getUserProfile() {
  const accessToken = localStorage.getItem('access_token');
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/users/profile/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      }
    });

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    console.error('Error:', error);
    return { success: false, error };
  }
}
```

---

## 🔄 Step 4: Refresh Token

Access tokens expire after 1 hour. Use refresh token to get a new access token:

### Endpoint
```
POST http://127.0.0.1:8000/api/users/token/refresh/
```

### Request Body
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Response
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Frontend Code Example
```javascript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/users/token/refresh/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh: refreshToken
      })
    });

    const data = await response.json();
    
    if (data.access) {
      localStorage.setItem('access_token', data.access);
      return { success: true, token: data.access };
    }
  } catch (error) {
    console.error('Error refreshing token:', error);
    return { success: false, error };
  }
}
```

---

## 🚪 Step 5: Logout

### Endpoint
```
POST http://127.0.0.1:8000/api/users/logout/
```

### Request Headers
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

### Request Body
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Response
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### Frontend Code Example
```javascript
async function logout() {
  const accessToken = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/users/logout/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh: refreshToken
      })
    });

    const data = await response.json();
    
    if (data.success) {
      // Clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      
      return { success: true };
    }
  } catch (error) {
    console.error('Error logging out:', error);
    return { success: false, error };
  }
}
```

---

## 📝 Complete React Component Example

```javascript
import React, { useState } from 'react';

function PhoneAuth() {
  const [phone, setPhone] = useState('+880');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState('phone'); // 'phone' or 'otp'
  const [loading, setLoading] = useState(false);

  const handleSendOTP = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/users/send-otp/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone })
      });

      const data = await response.json();

      if (data.success) {
        alert('OTP sent to your phone!');
        setStep('otp');
      } else {
        alert('Error: ' + JSON.stringify(data));
      }
    } catch (error) {
      alert('Network error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/users/verify-otp/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, otp })
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        alert('Login successful!');
        window.location.href = '/dashboard';
      } else {
        alert('Invalid OTP: ' + JSON.stringify(data));
      }
    } catch (error) {
      alert('Network error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px' }}>
      <h2>Phone Authentication</h2>

      {step === 'phone' ? (
        <form onSubmit={handleSendOTP}>
          <div style={{ marginBottom: '15px' }}>
            <label>Phone Number</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+8801719159900"
              style={{ width: '100%', padding: '10px', fontSize: '16px' }}
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{ width: '100%', padding: '12px', fontSize: '16px' }}
          >
            {loading ? 'Sending...' : 'Send OTP'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOTP}>
          <div style={{ marginBottom: '15px' }}>
            <label>Enter OTP</label>
            <input
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              placeholder="123456"
              maxLength={6}
              style={{ width: '100%', padding: '10px', fontSize: '16px' }}
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{ width: '100%', padding: '12px', fontSize: '16px' }}
          >
            {loading ? 'Verifying...' : 'Verify OTP'}
          </button>
          <button
            type="button"
            onClick={() => setStep('phone')}
            style={{ width: '100%', padding: '12px', marginTop: '10px' }}
          >
            Change Phone Number
          </button>
        </form>
      )}
    </div>
  );
}

export default PhoneAuth;
```

---

## ⚙️ Configuration Summary

### Backend Configuration
- **SMS Provider:** BulkSMS BD (http://bulksmsbd.net)
- **API Key:** `hYMFUDHeRp6chuAINbkZ`
- **Sender ID:** `8809617627045`
- **Base URL:** `http://127.0.0.1:8000/api/users/`
- **OTP Expiry:** 2 minutes (120 seconds)
- **OTP Length:** 6 digits
- **JWT Access Token:** 1 hour expiry
- **JWT Refresh Token:** 7 days expiry

### CORS Configuration
Make sure your frontend URL is added to `FRONTEND_URL` in `.env`:
```
FRONTEND_URL=http://localhost:3000
```

---

## 🧪 Testing with cURL

```bash
# Step 1: Send OTP
curl -X POST http://127.0.0.1:8000/api/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+8801719159900"}'

# Step 2: Verify OTP (use OTP from SMS or response)
curl -X POST http://127.0.0.1:8000/api/users/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+8801719159900", "otp": "123456"}'

# Step 3: Get Profile (use access token from verify response)
curl -X GET http://127.0.0.1:8000/api/users/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## ❓ Common Issues

### Issue 1: "Phone field is required"
**Solution:** Make sure you're sending `phone` in the request body, not `phoneNumber` or `phone_number`.

### Issue 2: "Invalid or expired OTP"
**Solution:** 
- OTP expires after 2 minutes
- OTP can only be used once
- Make sure you're using the latest OTP sent to the phone

### Issue 3: "CORS error"
**Solution:** Add your frontend URL to `FRONTEND_URL` in `.env` and restart the server.

### Issue 4: OTP not received on phone
**Solution:**
- Check if phone number format is correct (Bangladesh: +8801XXXXXXXXX)
- Verify BulkSMS BD API credentials in `.env`
- Check SMS logs in admin panel: http://127.0.0.1:8000/admin/notifications/smslog/

---

## 📊 SMS Logging

All SMS are logged in the database. Check them at:
```
http://127.0.0.1:8000/admin/notifications/smslog/
```

This shows:
- Recipient phone number
- Message content
- Status (sent/failed)
- Timestamp
- Error message (if failed)

---

## 🔒 Security Notes

1. **OTP Expiry:** OTPs expire after 2 minutes
2. **Single Use:** Each OTP can only be used once
3. **Rate Limiting:** Consider adding rate limiting to prevent abuse
4. **HTTPS:** Use HTTPS in production
5. **Token Storage:** Store JWT tokens securely (HttpOnly cookies recommended)
6. **Phone Verification:** Each phone number is automatically verified after successful OTP verification

---

## 📞 Need Help?

Check the SMS logs in Django admin panel to debug any SMS delivery issues.
