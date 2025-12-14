# 🚀 Quick Fix for Your React App

## ✅ Backend Status
- **Running at:** http://127.0.0.1:8000
- **CORS enabled for:** `localhost:3000`, `localhost:3001`, `localhost:5173`
- **Google auth:** Ready (needs Client ID)

---

## 🔴 Your Current Issues & Fixes

### 1. Google Client ID Error
```
[GSI_LOGGER]: The given client ID is not found.
```

**Fix in React `.env`:**
```env
VITE_GOOGLE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com
```

**Get Client ID:**
1. Go to https://console.cloud.google.com/
2. APIs & Services → Credentials
3. Create OAuth 2.0 Client ID
4. Add origins: `http://localhost:3001`

---

### 2. API Endpoints (Copy-Paste Ready)

```javascript
// src/config/api.js
export const API_BASE = 'http://127.0.0.1:8000';

export const API = {
  SEND_OTP: `${API_BASE}/api/users/send-otp/`,
  VERIFY_OTP: `${API_BASE}/api/users/verify-otp/`,
  GOOGLE_LOGIN: `${API_BASE}/api/users/google-login/`,
  PROFILE: `${API_BASE}/api/users/profile/`,
};
```

---

### 3. Send OTP Function

```javascript
// src/services/auth.js
export const sendOTP = async (phone) => {
  const response = await fetch('http://127.0.0.1:8000/api/users/send-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.phone?.[0] || 'Failed to send OTP');
  }
  
  return response.json();
};
```

---

### 4. Verify OTP Function

```javascript
export const verifyOTP = async (phone, otp, userData = {}) => {
  const response = await fetch('http://127.0.0.1:8000/api/users/verify-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone,
      otp,
      user_type: 'customer',
      ...userData
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.otp?.[0] || 'Invalid OTP');
  }
  
  const data = await response.json();
  
  // Save tokens
  localStorage.setItem('access_token', data.tokens.access);
  localStorage.setItem('refresh_token', data.tokens.refresh);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data;
};
```

---

### 5. Google Login Function

```javascript
export const googleLogin = async (googleToken) => {
  const response = await fetch('http://127.0.0.1:8000/api/users/google-login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      token: googleToken,
      user_type: 'customer'
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
};
```

---

### 6. Usage in Login Component

```jsx
import { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { sendOTP, verifyOTP, googleLogin } from '../services/auth';

function Login() {
  const [phone, setPhone] = useState('');
  const [otp, setOTP] = useState('');
  const [showOTP, setShowOTP] = useState(false);

  const handleSendOTP = async (e) => {
    e.preventDefault();
    try {
      const result = await sendOTP(phone);
      console.log('OTP:', result.otp); // For testing
      setShowOTP(true);
    } catch (error) {
      alert(error.message);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    try {
      await verifyOTP(phone, otp);
      window.location.href = '/dashboard';
    } catch (error) {
      alert(error.message);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      await googleLogin(credentialResponse.credential);
      window.location.href = '/dashboard';
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div>
      {!showOTP ? (
        <form onSubmit={handleSendOTP}>
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+1234567890"
          />
          <button type="submit">Send OTP</button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOTP}>
          <input
            value={otp}
            onChange={(e) => setOTP(e.target.value)}
            placeholder="Enter OTP"
            maxLength="6"
          />
          <button type="submit">Verify</button>
        </form>
      )}
      
      <GoogleLogin
        onSuccess={handleGoogleSuccess}
        onError={() => alert('Google login failed')}
      />
    </div>
  );
}
```

---

## 🧪 Test Backend Directly

Open browser console on your React app and run:

```javascript
// Test send OTP
fetch('http://127.0.0.1:8000/api/users/send-otp/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '+1234567890' })
})
.then(r => r.json())
.then(d => console.log('✅ Backend working! OTP:', d.otp));
```

**Expected output:**
```json
{
  "message": "OTP sent successfully",
  "phone": "+1234567890",
  "otp": "123456",
  "expires_in": "5 minutes"
}
```

---

## 📋 Checklist

- [ ] Backend running: `python manage.py runserver`
- [ ] Test API in browser console (see above)
- [ ] Add `VITE_API_BASE_URL=http://127.0.0.1:8000` to React `.env`
- [ ] Add `VITE_GOOGLE_CLIENT_ID=...` to React `.env`
- [ ] Install: `npm install @react-oauth/google`
- [ ] Remove double `/api/` from API calls
- [ ] Test send OTP
- [ ] Test verify OTP
- [ ] Test Google login

---

## 🆘 Still Having Issues?

### Check if backend is running:
```bash
curl http://127.0.0.1:8000/api/users/send-otp/
```

### Check CORS:
Open React app console → Network tab → Look for CORS errors

### Check API calls:
Add console.log to see what URL you're calling:
```javascript
const url = 'http://127.0.0.1:8000/api/users/send-otp/';
console.log('Calling:', url);
fetch(url, ...);
```

---

## 📞 Support

- Backend running on: `http://127.0.0.1:8000`
- Admin panel: `http://127.0.0.1:8000/admin/` (phone: +1234567890, password: admin123)
- API docs: `http://127.0.0.1:8000/swagger/`
