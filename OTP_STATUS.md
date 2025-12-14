# Quick Reference: OTP System Status

## ✅ Current Status

**Environment**: Development (DEBUG = True)  
**Behavior**: OTP is returned in API response for easy testing  
**Package Installed**: Twilio SDK ✅

---

## 🔄 API Behavior

### Current (Development Mode)
```bash
POST /api/users/send-otp/
{
  "phone": "+801719159900"
}

✅ Response:
{
  "phone": "+801719159900",
  "otp": "123456",              # ← OTP visible for testing
  "expires_in_seconds": 120
}
```

### Production (When DEBUG = False)
```bash
POST /api/users/send-otp/
{
  "phone": "+801719159900"
}

✅ Response:
{
  "phone": "+801719159900",
  "message": "OTP sent to your phone number",  # ← OTP sent via SMS
  "expires_in_seconds": 120
}
```

---

## 🚀 To Deploy to Production

1. **Get Twilio Account**
   - Sign up at https://www.twilio.com/
   - Get phone number ($1/month)
   - Copy Account SID & Auth Token

2. **Update settings.py**
   ```python
   DEBUG = False
   
   TWILIO_ACCOUNT_SID = 'your_real_account_sid'
   TWILIO_AUTH_TOKEN = 'your_real_auth_token'
   TWILIO_PHONE_NUMBER = '+1234567890'  # Your Twilio number
   
   ALLOWED_HOSTS = ['yourdomain.com']
   ```

3. **Setup Redis**
   ```bash
   # Install Redis
   # Update CACHES in settings.py with Redis URL
   ```

4. **That's it!** The system automatically switches to SMS delivery.

---

## 📊 What Changed

✅ **Twilio SDK installed** (9.8.8)  
✅ **SendOTPSerializer updated** with `_send_otp_via_sms()` method  
✅ **Automatic DEBUG detection** - switches between dev/prod modes  
✅ **Production-ready** - just needs Twilio credentials  

---

## 🔒 Security

- **Development**: OTP visible (OK for testing)
- **Production**: OTP never visible in response (sent via SMS only)
- **Both**: OTP expires in 2 minutes, can only be used once

---

For detailed explanation, see `OTP_DELIVERY_GUIDE.md`
