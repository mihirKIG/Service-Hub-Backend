// ====================================================================
// ServiceHub Backend API - React Frontend Integration Test
// ====================================================================

// IMPORTANT: Your frontend is calling WRONG endpoint!
// ❌ WRONG: http://127.0.0.1:8000/api/api/send-otp/ (double /api/)
// ✅ CORRECT: http://127.0.0.1:8000/api/users/send-otp/

const API_BASE_URL = 'http://127.0.0.1:8000';

// ====================================================================
// 1. SEND OTP TEST
// ====================================================================
async function testSendOTP() {
  console.log('Testing Send OTP...');
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/users/send-otp/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: '+1234567890'
      })
    });
    
    const data = await response.json();
    console.log('✅ Send OTP Success:', data);
    console.log('📱 OTP Code:', data.otp); // Save this for next test
    return data;
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

// ====================================================================
// 2. VERIFY OTP TEST
// ====================================================================
async function testVerifyOTP(phone, otp) {
  console.log('Testing Verify OTP...');
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/users/verify-otp/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: phone,
        otp: otp,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        user_type: 'customer'
      })
    });
    
    const data = await response.json();
    console.log('✅ Verify OTP Success:', data);
    console.log('🔑 Access Token:', data.tokens.access);
    console.log('🔄 Refresh Token:', data.tokens.refresh);
    return data;
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

// ====================================================================
// 3. GET PROFILE TEST (with JWT token)
// ====================================================================
async function testGetProfile(accessToken) {
  console.log('Testing Get Profile...');
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/users/profile/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      }
    });
    
    const data = await response.json();
    console.log('✅ Get Profile Success:', data);
    return data;
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

// ====================================================================
// RUN ALL TESTS
// ====================================================================
async function runAllTests() {
  console.log('🚀 Starting API Tests...\n');
  
  // Step 1: Send OTP
  const otpResult = await testSendOTP();
  console.log('\n---\n');
  
  if (otpResult && otpResult.otp) {
    // Step 2: Verify OTP
    const loginResult = await testVerifyOTP(otpResult.phone, otpResult.otp);
    console.log('\n---\n');
    
    if (loginResult && loginResult.tokens) {
      // Step 3: Get Profile with token
      await testGetProfile(loginResult.tokens.access);
    }
  }
  
  console.log('\n✅ All tests completed!');
}

// Run tests
runAllTests();

// ====================================================================
// EXAMPLE: React Component Integration
// ====================================================================
/*

// src/services/api.js
export const API_BASE_URL = 'http://127.0.0.1:8000';

export const authAPI = {
  sendOTP: async (phone) => {
    const response = await fetch(`${API_BASE_URL}/api/users/send-otp/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    if (!response.ok) throw new Error('Failed to send OTP');
    return response.json();
  },

  verifyOTP: async (phone, otp, userData) => {
    const response = await fetch(`${API_BASE_URL}/api/users/verify-otp/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, otp, ...userData })
    });
    if (!response.ok) throw new Error('Failed to verify OTP');
    return response.json();
  },

  getProfile: async (token) => {
    const response = await fetch(`${API_BASE_URL}/api/users/profile/`, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    if (!response.ok) throw new Error('Failed to get profile');
    return response.json();
  }
};

// Usage in React Component
import { authAPI } from './services/api';

function LoginComponent() {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState(1);

  const handleSendOTP = async () => {
    try {
      const result = await authAPI.sendOTP(phone);
      console.log('OTP:', result.otp); // For testing
      setStep(2);
    } catch (error) {
      console.error(error);
    }
  };

  const handleVerifyOTP = async () => {
    try {
      const result = await authAPI.verifyOTP(phone, otp, {
        first_name: 'John',
        user_type: 'customer'
      });
      
      localStorage.setItem('access_token', result.tokens.access);
      localStorage.setItem('refresh_token', result.tokens.refresh);
      
      // Redirect to dashboard
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      {step === 1 && (
        <>
          <input value={phone} onChange={(e) => setPhone(e.target.value)} />
          <button onClick={handleSendOTP}>Send OTP</button>
        </>
      )}
      {step === 2 && (
        <>
          <input value={otp} onChange={(e) => setOtp(e.target.value)} />
          <button onClick={handleVerifyOTP}>Verify</button>
        </>
      )}
    </div>
  );
}

*/
