"""
Test script for the new authentication system
Tests Phone OTP and Google Sign-In authentication

Run this script after starting the server:
python test_auth_endpoints.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/users"

def print_response(response, title):
    """Print formatted API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_send_otp():
    """Test OTP generation and sending"""
    print("\n\n🔥 TEST 1: Send OTP")
    data = {
        "phone": "+919876543210"
    }
    response = requests.post(f"{API_BASE}/send-otp/", json=data)
    print_response(response, "Send OTP API")
    return response.json().get('otp') if response.status_code == 200 else None

def test_verify_otp(phone, otp):
    """Test OTP verification and user login/registration"""
    print("\n\n🔥 TEST 2: Verify OTP & Auto Login")
    data = {
        "phone": phone,
        "otp": otp
    }
    response = requests.post(f"{API_BASE}/verify-otp/", json=data)
    print_response(response, "Verify OTP API")
    return response.json().get('access') if response.status_code == 200 else None

def test_user_profile(access_token):
    """Test authenticated user profile retrieval"""
    print("\n\n🔥 TEST 3: Get User Profile (Authenticated)")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{API_BASE}/profile/", headers=headers)
    print_response(response, "User Profile API")

def test_update_profile(access_token):
    """Test profile update"""
    print("\n\n🔥 TEST 4: Update User Profile")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com"
    }
    response = requests.patch(f"{API_BASE}/profile/", json=data, headers=headers)
    print_response(response, "Update Profile API")

def test_invalid_otp():
    """Test invalid OTP verification"""
    print("\n\n🔥 TEST 5: Invalid OTP Verification")
    data = {
        "phone": "+919876543210",
        "otp": "000000"
    }
    response = requests.post(f"{API_BASE}/verify-otp/", json=data)
    print_response(response, "Invalid OTP API")

def test_expired_otp():
    """Test expired OTP (after 2 minutes)"""
    print("\n\n🔥 TEST 6: Expired OTP (Wait 2 minutes after generating)")
    print("Note: This test requires manual timing")
    print("1. Generate OTP")
    print("2. Wait for 2+ minutes")
    print("3. Try to verify - should fail")

def test_google_auth_invalid():
    """Test Google Sign-In with invalid token"""
    print("\n\n🔥 TEST 7: Google Sign-In (Invalid Token)")
    data = {
        "id_token": "invalid_token_12345"
    }
    response = requests.post(f"{API_BASE}/google/", json=data)
    print_response(response, "Google Sign-In API (Invalid Token)")

def main():
    """Run all authentication tests"""
    print("\n" + "="*60)
    print("🚀 SERVICEHUB AUTHENTICATION SYSTEM TEST")
    print("="*60)
    print("\nAuthentication Methods:")
    print("1. Phone OTP (Cache-based, 2-minute expiry)")
    print("2. Google Sign-In (ID Token verification)")
    print("\nServer: http://127.0.0.1:8000")
    
    try:
        # Test 1: Send OTP
        otp = test_send_otp()
        
        if otp:
            # Test 2: Verify OTP and get access token
            access_token = test_verify_otp("+919876543210", otp)
            
            if access_token:
                # Test 3: Get user profile
                test_user_profile(access_token)
                
                # Test 4: Update profile
                test_update_profile(access_token)
        
        # Test 5: Invalid OTP
        test_invalid_otp()
        
        # Test 6: Expired OTP (manual)
        test_expired_otp()
        
        # Test 7: Google Auth with invalid token
        test_google_auth_invalid()
        
        print("\n\n" + "="*60)
        print("✅ TESTS COMPLETED")
        print("="*60)
        print("\nTo test Google Sign-In properly:")
        print("1. Get a valid Google ID Token from your frontend")
        print("2. Use it in POST /api/users/google/ with {'id_token': '<token>'}")
        print("\nTo test OTP expiry:")
        print("1. Generate OTP using /api/users/send-otp/")
        print("2. Wait for 2+ minutes")
        print("3. Try verifying - it should fail")
        
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        print("Make sure the server is running at http://127.0.0.1:8000")

if __name__ == "__main__":
    main()
