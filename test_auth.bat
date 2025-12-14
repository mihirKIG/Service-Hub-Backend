@echo off
REM ServiceHub Authentication System - Quick Test Script (Windows)
REM Run this script to test all authentication endpoints

setlocal enabledelayedexpansion

set BASE_URL=http://127.0.0.1:8000/api/users
set TEST_PHONE=+919876543210

echo ======================================================
echo   ServiceHub Authentication System - Quick Test
echo ======================================================
echo.

REM Test 1: Send OTP
echo TEST 1: Sending OTP to %TEST_PHONE%
echo ------------------------------------------------------
curl -s -X POST "%BASE_URL%/send-otp/" -H "Content-Type: application/json" -d "{\"phone\":\"%TEST_PHONE%\"}" > otp_response.json

type otp_response.json
echo.
echo Generated OTP - Check response above
echo.
pause

REM Test 2: Verify OTP (You'll need to enter the OTP manually)
echo TEST 2: Verifying OTP and Logging In
echo ------------------------------------------------------
set /p OTP="Enter the OTP from above: "

curl -s -X POST "%BASE_URL%/verify-otp/" -H "Content-Type: application/json" -d "{\"phone\":\"%TEST_PHONE%\",\"otp\":\"%OTP%\"}" > login_response.json

type login_response.json
echo.
pause

REM Extract access token (manual for now)
echo TEST 3: Getting User Profile
echo ------------------------------------------------------
set /p ACCESS_TOKEN="Enter the access token from above: "

curl -s -X GET "%BASE_URL%/profile/" -H "Authorization: Bearer %ACCESS_TOKEN%"
echo.
echo.
pause

REM Test 4: Update Profile
echo TEST 4: Updating User Profile
echo ------------------------------------------------------
curl -s -X PATCH "%BASE_URL%/profile/" -H "Authorization: Bearer %ACCESS_TOKEN%" -H "Content-Type: application/json" -d "{\"first_name\":\"Test\",\"last_name\":\"User\",\"email\":\"test@example.com\"}"
echo.
echo.
pause

REM Test 5: Refresh Token
echo TEST 5: Refreshing Access Token
echo ------------------------------------------------------
set /p REFRESH_TOKEN="Enter the refresh token from login response: "

curl -s -X POST "%BASE_URL%/token/refresh/" -H "Content-Type: application/json" -d "{\"refresh\":\"%REFRESH_TOKEN%\"}"
echo.
echo.
pause

REM Test 6: Logout
echo TEST 6: Logging Out
echo ------------------------------------------------------
curl -s -X POST "%BASE_URL%/logout/" -H "Authorization: Bearer %ACCESS_TOKEN%" -H "Content-Type: application/json" -d "{\"refresh\":\"%REFRESH_TOKEN%\"}"
echo.
echo.

echo.
echo ======================================================
echo   All Tests Completed!
echo ======================================================
echo.
echo Authentication Endpoints:
echo   [✓] POST /api/users/send-otp/ - Generate OTP
echo   [✓] POST /api/users/verify-otp/ - Verify OTP ^& Login
echo   [✓] GET /api/users/profile/ - Get User Profile
echo   [✓] PATCH /api/users/profile/ - Update Profile
echo   [✓] POST /api/users/token/refresh/ - Refresh JWT Token
echo   [✓] POST /api/users/logout/ - Logout ^& Blacklist Token
echo.
echo For Google Sign-In testing, see AUTHENTICATION_DOCS.md
echo.

REM Cleanup
del otp_response.json
del login_response.json

pause
