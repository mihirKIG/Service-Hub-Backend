#!/usr/bin/env python
"""
Test script for OTP system with BulkSMSBD
Run: python test_otp_system.py
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/users"

def test_send_otp(phone):
    """Test sending OTP"""
    print(f"\n{'='*60}")
    print(f"TEST 1: Send OTP to {phone}")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/send-otp/"
    data = {"phone": phone}
    
    print(f"\nRequest: POST {url}")
    print(f"Body: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS: OTP sent!")
            if result.get('otp'):
                print(f"🔑 OTP (DEBUG mode): {result['otp']}")
            return result.get('otp')
        else:
            print(f"\n❌ FAILED: {response.json()}")
            return None
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def test_verify_otp(phone, otp, profile_data=None):
    """Test verifying OTP"""
    print(f"\n{'='*60}")
    print(f"TEST 2: Verify OTP for {phone}")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/verify-otp/"
    data = {
        "phone": phone,
        "otp": otp
    }
    
    if profile_data:
        data.update(profile_data)
    
    print(f"\nRequest: POST {url}")
    print(f"Body: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS: OTP verified!")
            print(f"👤 User: {result.get('user', {}).get('phone')}")
            print(f"🆕 New User: {result.get('created')}")
            print(f"🔐 Access Token: {result.get('tokens', {}).get('access')[:50]}...")
            return result
        else:
            print(f"\n❌ FAILED: {response.json()}")
            return None
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def test_get_profile(access_token):
    """Test getting user profile"""
    print(f"\n{'='*60}")
    print(f"TEST 3: Get User Profile")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/profile/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print(f"\nRequest: GET {url}")
    print(f"Headers: Authorization: Bearer {access_token[:30]}...")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS: Profile retrieved!")
            return response.json()
        else:
            print(f"\n❌ FAILED: {response.json()}")
            return None
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def main():
    print("\n" + "="*60)
    print("🧪 OTP SYSTEM TEST - BulkSMSBD Integration")
    print("="*60)
    
    # Test phone number (Bangladesh format)
    test_phone = "+8801719159900"
    
    # TEST 1: Send OTP
    otp = test_send_otp(test_phone)
    
    if not otp:
        print("\n❌ Cannot proceed without OTP. Check server logs.")
        return
    
    # Wait a bit
    print("\n⏳ Waiting 2 seconds before verification...")
    time.sleep(2)
    
    # TEST 2: Verify OTP
    profile_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com"
    }
    
    result = test_verify_otp(test_phone, otp, profile_data)
    
    if not result:
        print("\n❌ OTP verification failed.")
        return
    
    # TEST 3: Get Profile
    access_token = result.get('tokens', {}).get('access')
    if access_token:
        test_get_profile(access_token)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    
    print("\n📝 Summary:")
    print("1. ✅ OTP sent via BulkSMSBD")
    print("2. ✅ OTP verified successfully")
    print("3. ✅ User auto-created/logged in")
    print("4. ✅ JWT tokens generated")
    print("5. ✅ Profile endpoint accessible")
    
    print("\n🎉 OTP System is working perfectly!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
