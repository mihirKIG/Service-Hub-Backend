#!/bin/bash

echo "🧪 Testing OTP System"
echo "===================="
echo ""

# Test 1: Send OTP
echo "📱 Sending OTP to +801719159900..."
response=$(curl -s -X POST http://127.0.0.1:8000/api/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+801719159900"}')

echo "Response:"
echo "$response" | python -m json.tool 2>/dev/null || echo "$response"
echo ""

# Extract OTP if visible (DEBUG mode)
otp=$(echo "$response" | python -c "import sys, json; print(json.load(sys.stdin).get('otp', 'Not visible'))" 2>/dev/null)

if [ "$otp" != "Not visible" ] && [ "$otp" != "" ]; then
    echo "✅ OTP visible in response (DEBUG mode): $otp"
    echo ""
    echo "📋 This means:"
    echo "  • You're in DEBUG mode (good for testing)"
    echo "  • OTP is NOT being sent via SMS"
    echo "  • To send real SMS, add Twilio credentials to .env"
    echo ""
    echo "🔧 To send real SMS:"
    echo "  1. Sign up at https://www.twilio.com/try-twilio"
    echo "  2. Get your credentials from https://console.twilio.com/"
    echo "  3. Update .env file with:"
    echo "     TWILIO_ACCOUNT_SID=ACxxxxx..."
    echo "     TWILIO_AUTH_TOKEN=xxxxx..."
    echo "     TWILIO_PHONE_NUMBER=+1xxxxx..."
    echo "  4. Restart server"
else
    echo "📧 OTP sent via SMS (Production mode)"
    echo "Check your phone for the verification code!"
fi

echo ""
echo "===================="
