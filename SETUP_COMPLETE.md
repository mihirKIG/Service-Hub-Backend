# ✅ Phone OTP Authentication - Setup Complete!

## 🎉 What's Been Configured

### 1. SMS Provider Integration
- **Provider:** BulkSMS BD (http://bulksmsbd.net)
- **API Key:** `hYMFUDHeRp6chuAINbkZ`
- **Sender ID:** `8809617627045`
- **Format:** Bangladesh phone numbers (+880...)

### 2. Files Modified

#### `.env`
```dotenv
BULKSMS_API_KEY=hYMFUDHeRp6chuAINbkZ
BULKSMS_SENDER_ID=8809617627045
BULKSMS_API_URL=http://bulksmsbd.net/api/smsapi
```

#### `servicehub_backend/settings.py`
```python
BULKSMS_API_KEY = os.getenv('BULKSMS_API_KEY', '')
BULKSMS_SENDER_ID = os.getenv('BULKSMS_SENDER_ID', '')
BULKSMS_API_URL = os.getenv('BULKSMS_API_URL', 'http://bulksmsbd.net/api/smsapi')
```

#### `utils/sms.py`
- Removed Twilio integration
- Added BulkSMS BD HTTP API integration
- Handles Bangladesh phone number formats (+880, 880, 01...)
- Logs all SMS to database

### 3. Database Migration
- Added `google_uid` column to users table
- Migration: `users/migrations/0002_add_google_uid.py`
- Status: Applied ✅

---

## 🚀 How It Works

### Flow for Frontend

```
1. User enters phone number (+8801719159900)
   ↓
2. Frontend calls: POST /api/users/send-otp/
   ↓
3. Backend generates 6-digit OTP
   ↓
4. OTP stored in cache (2 minutes)
   ↓
5. SMS sent via BulkSMS BD API
   ↓
6. User receives SMS with OTP
   ↓
7. User enters OTP in frontend
   ↓
8. Frontend calls: POST /api/users/verify-otp/
   ↓
9. Backend verifies OTP
   ↓
10. If valid: User logged in/registered
   ↓
11. Backend returns JWT tokens
   ↓
12. Frontend stores tokens and redirects to dashboard
```

---

## 📋 API Endpoints

### 1. Send OTP
```
POST http://127.0.0.1:8000/api/users/send-otp/
Content-Type: application/json

{
  "phone": "+8801719159900"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "phone": "+8801719159900",
  "otp": "123456",
  "expires_in_seconds": 120
}
```

### 2. Verify OTP
```
POST http://127.0.0.1:8000/api/users/verify-otp/
Content-Type: application/json

{
  "phone": "+8801719159900",
  "otp": "123456",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com"
}
```

**Response:**
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
    "is_verified": true
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### 3. Get Profile (Protected)
```
GET http://127.0.0.1:8000/api/users/profile/
Authorization: Bearer <access_token>
```

### 4. Refresh Token
```
POST http://127.0.0.1:8000/api/users/token/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

### 5. Logout
```
POST http://127.0.0.1:8000/api/users/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

---

## 🧪 Testing

### Start Server
```bash
cd D:/servicehub
python manage.py runserver
```

### Test Send OTP
```bash
curl -X POST http://127.0.0.1:8000/api/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+8801719159900"}'
```

### Check SMS Logs
```
http://127.0.0.1:8000/admin/notifications/smslog/
```

---

## 📚 Documentation Created

1. **FRONTEND_PHONE_AUTH_GUIDE.md** - Complete frontend integration guide
   - All API endpoints with examples
   - React component examples
   - cURL test commands
   - Common issues and solutions

2. **OTP_FIXED.md** - Original OTP implementation guide

3. **WHY_NO_SMS.md** - Explanation of DEBUG mode vs production

---

## ⚙️ Configuration Details

### OTP Settings
- **Length:** 6 digits
- **Expiry:** 2 minutes (120 seconds)
- **Storage:** Django cache (in-memory for dev, Redis for production)
- **Single use:** OTP deleted after successful verification

### JWT Settings
- **Access Token:** 1 hour expiry
- **Refresh Token:** 7 days expiry
- **Blacklist:** Enabled (tokens blacklisted on logout)

### Phone Number Format
- **Accepted formats:**
  - `+8801719159900` (E.164 format - recommended)
  - `8801719159900`
  - `01719159900`
- **Stored format:** `+8801719159900` (with country code)

---

## 🔍 Monitoring & Debugging

### Check SMS Status
All SMS are logged in the database. Access the admin panel:
```
http://127.0.0.1:8000/admin/notifications/smslog/
```

You can see:
- Recipient phone number
- Message content
- Status (sent/failed)
- Error message (if failed)
- Timestamp

### Common Issues

**Issue: "Column google_uid does not exist"**
- ✅ Fixed: Migration added and applied

**Issue: "SMS not received"**
- Check phone number format
- Check SMS logs in admin panel
- Verify BulkSMS BD API credentials
- Check BulkSMS BD account balance

**Issue: "Invalid or expired OTP"**
- OTP expires after 2 minutes
- OTP can only be used once
- Make sure using the latest OTP

---

## 🎯 Next Steps for Frontend

1. **Create Login Page**
   - Phone number input
   - OTP input
   - Submit buttons

2. **Implement API Calls**
   - Send OTP on phone submit
   - Verify OTP on OTP submit
   - Store JWT tokens in localStorage or cookies

3. **Add Protected Routes**
   - Check for access token before rendering
   - Redirect to login if no token
   - Refresh token before expiry

4. **Handle Token Expiry**
   - Detect 401 responses
   - Auto-refresh access token using refresh token
   - Logout if refresh token expired

---

## 📞 Testing Credentials

**Test Phone Number:** `+8801719159900`

**API Base URL:** `http://127.0.0.1:8000/api/users/`

**Admin Panel:** `http://127.0.0.1:8000/admin/`

---

## ✅ Checklist

- [x] BulkSMS BD API integrated
- [x] OTP generation and caching
- [x] SMS sending via HTTP API
- [x] Phone number format handling
- [x] User registration/login flow
- [x] JWT token generation
- [x] Token refresh endpoint
- [x] Logout with token blacklist
- [x] SMS logging to database
- [x] Database migration (google_uid)
- [x] Complete documentation
- [x] API testing examples

---

## 🚨 Important Notes

1. **DEBUG Mode:** Currently OTP is returned in API response for easy testing. In production (DEBUG=False), OTP will NOT be returned.

2. **Phone Verification:** All registered users are automatically marked as verified after successful OTP verification.

3. **SMS Costs:** Check your BulkSMS BD account for pricing and balance.

4. **Rate Limiting:** Consider adding rate limiting to prevent OTP abuse.

5. **Security:** Always use HTTPS in production.

---

## 📖 Full Documentation

See `FRONTEND_PHONE_AUTH_GUIDE.md` for:
- Detailed API documentation
- Complete React examples
- Error handling
- Best practices
- Security considerations

---

**Everything is ready for frontend integration!** 🎉

Start your Django server and begin testing with your frontend application.

```bash
cd D:/servicehub
python manage.py runserver
```

Then test from your React/frontend app:
```javascript
fetch('http://127.0.0.1:8000/api/users/send-otp/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({phone: '+8801719159900'})
})
```
