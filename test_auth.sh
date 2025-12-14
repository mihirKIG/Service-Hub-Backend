#!/bin/bash

# ServiceHub Authentication System - Quick Test Script
# Run this script to test all authentication endpoints

BASE_URL="http://127.0.0.1:8000/api/users"
TEST_PHONE="+919876543210"

echo "======================================================"
echo "  ServiceHub Authentication System - Quick Test"
echo "======================================================"
echo ""

# Test 1: Send OTP
echo "TEST 1: Sending OTP to $TEST_PHONE"
echo "------------------------------------------------------"
OTP_RESPONSE=$(curl -s -X POST "$BASE_URL/send-otp/" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"$TEST_PHONE\"}")

echo "$OTP_RESPONSE" | python -m json.tool
OTP=$(echo "$OTP_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('otp', ''))")
echo ""
echo "Generated OTP: $OTP"
echo ""

# Test 2: Verify OTP and Login
if [ -n "$OTP" ]; then
    echo "TEST 2: Verifying OTP and Logging In"
    echo "------------------------------------------------------"
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/verify-otp/" \
      -H "Content-Type: application/json" \
      -d "{\"phone\":\"$TEST_PHONE\",\"otp\":\"$OTP\"}")
    
    echo "$LOGIN_RESPONSE" | python -m json.tool
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('access', ''))")
    REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('refresh', ''))")
    echo ""
    echo "Access Token: ${ACCESS_TOKEN:0:50}..."
    echo "Refresh Token: ${REFRESH_TOKEN:0:50}..."
    echo ""
    
    # Test 3: Get User Profile
    if [ -n "$ACCESS_TOKEN" ]; then
        echo "TEST 3: Getting User Profile"
        echo "------------------------------------------------------"
        curl -s -X GET "$BASE_URL/profile/" \
          -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool
        echo ""
        echo ""
        
        # Test 4: Update Profile
        echo "TEST 4: Updating User Profile"
        echo "------------------------------------------------------"
        curl -s -X PATCH "$BASE_URL/profile/" \
          -H "Authorization: Bearer $ACCESS_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"first_name":"Test","last_name":"User","email":"test@example.com"}' | python -m json.tool
        echo ""
        echo ""
        
        # Test 5: Refresh Token
        echo "TEST 5: Refreshing Access Token"
        echo "------------------------------------------------------"
        curl -s -X POST "$BASE_URL/token/refresh/" \
          -H "Content-Type: application/json" \
          -d "{\"refresh\":\"$REFRESH_TOKEN\"}" | python -m json.tool
        echo ""
        echo ""
        
        # Test 6: Logout
        echo "TEST 6: Logging Out"
        echo "------------------------------------------------------"
        curl -s -X POST "$BASE_URL/logout/" \
          -H "Authorization: Bearer $ACCESS_TOKEN" \
          -H "Content-Type: application/json" \
          -d "{\"refresh\":\"$REFRESH_TOKEN\"}" | python -m json.tool
        echo ""
    fi
fi

echo ""
echo "======================================================"
echo "  All Tests Completed!"
echo "======================================================"
echo ""
echo "Authentication Endpoints:"
echo "  ✅ POST /api/users/send-otp/ - Generate OTP"
echo "  ✅ POST /api/users/verify-otp/ - Verify OTP & Login"
echo "  ✅ GET /api/users/profile/ - Get User Profile"
echo "  ✅ PATCH /api/users/profile/ - Update Profile"
echo "  ✅ POST /api/users/token/refresh/ - Refresh JWT Token"
echo "  ✅ POST /api/users/logout/ - Logout & Blacklist Token"
echo ""
echo "For Google Sign-In testing, see AUTHENTICATION_DOCS.md"
echo ""
