# Test Authentication Endpoints

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/users"

def test_send_otp():
    """Test sending OTP"""
    print("\n1. Testing Send OTP...")
    response = requests.post(
        f"{BASE_URL}/send-otp/",
        json={"phone": "+1234567890"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_verify_otp(phone, otp):
    """Test verifying OTP and login"""
    print("\n2. Testing Verify OTP...")
    response = requests.post(
        f"{BASE_URL}/verify-otp/",
        json={
            "phone": phone,
            "otp": otp,
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "user_type": "customer"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_get_profile(access_token):
    """Test getting user profile"""
    print("\n3. Testing Get Profile...")
    response = requests.get(
        f"{BASE_URL}/profile/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_update_profile(access_token):
    """Test updating user profile"""
    print("\n4. Testing Update Profile...")
    response = requests.patch(
        f"{BASE_URL}/profile/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_token_refresh(refresh_token):
    """Test refreshing access token"""
    print("\n5. Testing Token Refresh...")
    response = requests.post(
        f"{BASE_URL}/token/refresh/",
        json={"refresh": refresh_token}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

if __name__ == "__main__":
    print("="*50)
    print("ServiceHub Authentication API Tests")
    print("="*50)
    
    try:
        # Test 1: Send OTP
        otp_data = test_send_otp()
        phone = otp_data.get('phone')
        otp = otp_data.get('otp')
        
        if phone and otp:
            # Test 2: Verify OTP
            verify_data = test_verify_otp(phone, otp)
            access_token = verify_data.get('tokens', {}).get('access')
            refresh_token = verify_data.get('tokens', {}).get('refresh')
            
            if access_token:
                # Test 3: Get Profile
                test_get_profile(access_token)
                
                # Test 4: Update Profile
                test_update_profile(access_token)
                
                # Test 5: Refresh Token
                if refresh_token:
                    test_token_refresh(refresh_token)
        
        print("\n" + "="*50)
        print("All tests completed!")
        print("="*50)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Make sure the Django server is running on http://127.0.0.1:8000")
