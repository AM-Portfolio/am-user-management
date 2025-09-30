# 🧪 Postman API Testing Collection - AM User Management

This document provides a complete list of API endpoints for testing the AM User Management system in Postman, including request/response examples and test scenarios.

## 📋 **Table of Contents**
1. [Current Working APIs](#current-working-apis)
2. [Production APIs (To Implement)](#production-apis-to-implement)
3. [Postman Collection Setup](#postman-collection-setup)
4. [Environment Variables](#environment-variables)
5. [Test Scenarios](#test-scenarios)

---

## 🟢 **Current Working APIs**

These APIs are **currently functional** and ready for testing:

### 1. **Health Check**
```http
GET {{base_url}}/health
```
**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-09-30T12:46:49.029523+00:00"
}
```

### 2. **Authentication Status**
```http
GET {{base_url}}/api/v1/auth/status
```
**Response:**
```json
{
  "status": "Account management module fully integrated",
  "features": [
    "User registration with email verification",
    "User authentication with password hashing",
    "Domain events publishing",
    "Database persistence"
  ]
}
```

### 3. **User Registration** ✅
```http
POST {{base_url}}/api/v1/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}
```
**Success Response (201):**
```json
{
  "user_id": "c381d32f-2cb6-4107-aeb6-e9e9d6eff1e7",
  "email": "test@example.com",
  "status": "pending_verification",
  "created_at": "2025-09-30T12:46:27.349842+00:00"
}
```
**Error Response (409 - Email Exists):**
```json
{
  "detail": {
    "message": "Email already exists: test@example.com",
    "type": "email_already_exists",
    "field": "email"
  }
}
```

### 4. **User Login** ✅
```http
POST {{base_url}}/api/v1/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "securePassword123"
}
```
**Success Response (200):**
```json
{
  "user_id": "c381d32f-2cb6-4107-aeb6-e9e9d6eff1e7",
  "email": "test@example.com",
  "status": "active",
  "session_id": "session_c381d32f-2cb6-4107-aeb6-e9e9d6eff1e7_1759236298",
  "last_login_at": "2025-09-30T12:44:58.538015+00:00",
  "requires_verification": false
}
```
**Error Response (401 - Invalid Credentials):**
```json
{
  "detail": "Invalid email or password"
}
```
**Error Response (403 - Email Not Verified):**
```json
{
  "detail": {
    "message": "Email not verified: test@example.com",
    "type": "email_not_verified",
    "requires_verification": true
  }
}
```

### 5. **Password Reset Request** 🚧
```http
POST {{base_url}}/api/v1/auth/password-reset
Content-Type: application/json

{
  "email": "test@example.com"
}
```
**Note:** Currently returns "Password reset not implemented yet"

### 6. **Email Verification** 🚧
```http
GET {{base_url}}/api/v1/auth/verify-email?token=verification_token_here
```
**Note:** Currently returns "Email verification not implemented yet"

### 7. **User Logout** 🚧
```http
POST {{base_url}}/api/v1/auth/logout
```
**Note:** Currently returns "Logout successful" (mock implementation)

---

## 🔄 **Production APIs (To Implement)**

These APIs are described in the production guide and ready for implementation:

### 8. **Email Verification** (Production)
```http
GET {{base_url}}/api/v1/auth/verify-email?token={{verification_token}}
```
**Success Response:**
```json
{
  "message": "Email verified successfully",
  "user_id": "user-uuid",
  "verified_at": "2025-09-30T12:44:58.538015+00:00"
}
```
**Error Responses:**
```json
// Invalid Token (400)
{
  "detail": {
    "message": "Invalid or expired verification token",
    "type": "invalid_token"
  }
}

// Token Expired (410)
{
  "detail": {
    "message": "Verification token has expired",
    "type": "token_expired"
  }
}
```

### 9. **Resend Verification Email**
```http
POST {{base_url}}/api/v1/auth/resend-verification
Content-Type: application/json

{
  "email": "test@example.com"
}
```
**Success Response:**
```json
{
  "message": "Verification email sent successfully",
  "email": "test@example.com"
}
```

### 10. **Refresh Token**
```http
POST {{base_url}}/api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "refresh_token_here"
}
```
**Success Response:**
```json
{
  "access_token": "new_access_token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 11. **Change Password**
```http
POST {{base_url}}/api/v1/auth/change-password
Content-Type: application/json
Authorization: Bearer {{access_token}}

{
  "current_password": "oldPassword123",
  "new_password": "newPassword456",
  "confirm_password": "newPassword456"
}
```
**Success Response:**
```json
{
  "message": "Password changed successfully"
}
```

### 12. **Get User Profile** (Protected)
```http
GET {{base_url}}/api/v1/users/me
Authorization: Bearer {{access_token}}
```
**Success Response:**
```json
{
  "user_id": "user-uuid",
  "email": "test@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "status": "active",
  "email_verified": true,
  "created_at": "2025-09-30T12:44:58.538015+00:00",
  "last_login_at": "2025-09-30T12:44:58.538015+00:00"
}
```

### 13. **Update User Profile** (Protected)
```http
PATCH {{base_url}}/api/v1/users/me
Content-Type: application/json
Authorization: Bearer {{access_token}}

{
  "first_name": "John Updated",
  "last_name": "Doe Updated",
  "phone_number": "+1987654321"
}
```

### 14. **Delete User Account** (Protected)
```http
DELETE {{base_url}}/api/v1/users/me
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "password": "confirmPassword123"
}
```

---

## ⚙️ **Postman Collection Setup**

### Environment Variables
Create a Postman environment with these variables:

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "refresh_token": "",
  "user_id": "",
  "verification_token": "",
  "test_email": "postman_test@example.com",
  "test_password": "PostmanTest123!"
}
```

### Pre-request Scripts

**For Authentication Endpoints:**
```javascript
// Generate random test email
const randomString = Math.random().toString(36).substring(7);
pm.environment.set("random_email", `test_${randomString}@example.com`);

// Set timestamp
pm.environment.set("timestamp", new Date().toISOString());
```

**For Protected Endpoints:**
```javascript
// Check if access token exists
const accessToken = pm.environment.get("access_token");
if (!accessToken) {
    throw new Error("Access token required. Please login first.");
}
```

### Test Scripts

**For Registration Endpoint:**
```javascript
pm.test("Registration successful", function () {
    pm.response.to.have.status(201);
    
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property("user_id");
    pm.expect(responseJson).to.have.property("email");
    pm.expect(responseJson.status).to.equal("pending_verification");
    
    // Save user_id for later tests
    pm.environment.set("user_id", responseJson.user_id);
});

pm.test("Response time is less than 2000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});
```

**For Login Endpoint:**
```javascript
pm.test("Login successful", function () {
    pm.response.to.have.status(200);
    
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property("session_id");
    pm.expect(responseJson).to.have.property("user_id");
    
    // Save session for later use
    pm.environment.set("session_id", responseJson.session_id);
    
    // If using JWT (production), save tokens
    if (responseJson.access_token) {
        pm.environment.set("access_token", responseJson.access_token);
    }
    if (responseJson.refresh_token) {
        pm.environment.set("refresh_token", responseJson.refresh_token);
    }
});

pm.test("User status is active", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson.status).to.equal("active");
});
```

---

## 🧪 **Test Scenarios**

### **Scenario 1: Complete User Registration Flow**
1. **Register New User** → Should return `pending_verification`
2. **Login with Unverified User** → Should fail with `403 Forbidden`
3. **Manually Verify User** (Database update for testing)
4. **Login with Verified User** → Should succeed

### **Scenario 2: Authentication Edge Cases**
1. **Register with Existing Email** → Should return `409 Conflict`
2. **Login with Invalid Email** → Should return `401 Unauthorized`
3. **Login with Wrong Password** → Should return `401 Unauthorized`
4. **Login with Valid Credentials** → Should return `200 OK`

### **Scenario 3: Password Security**
1. **Register with Weak Password** → Should return validation errors
2. **Register with Strong Password** → Should succeed
3. **Test Password Hashing** → Verify passwords are hashed (check database)

### **Scenario 4: Rate Limiting** (Production)
1. **Make 10+ Rapid Requests** → Should return `429 Too Many Requests`
2. **Wait for Rate Limit Reset** → Should work normally again

### **Scenario 5: Token Management** (Production)
1. **Login and Get Tokens** → Save access and refresh tokens
2. **Use Access Token** → Should work for protected endpoints
3. **Use Expired Token** → Should return `401 Unauthorized`
4. **Refresh Tokens** → Should get new access token

---

## 📊 **Collection Organization**

### **Folder Structure:**
```
📁 AM User Management API
├── 📁 Authentication
│   ├── 🟢 Register User
│   ├── 🟢 Login User
│   ├── 🔄 Refresh Token
│   ├── 🔄 Verify Email
│   ├── 🔄 Resend Verification
│   ├── 🔄 Change Password
│   └── 🔄 Logout
├── 📁 User Management
│   ├── 🔄 Get Profile
│   ├── 🔄 Update Profile
│   └── 🔄 Delete Account
├── 📁 System
│   ├── 🟢 Health Check
│   └── 🟢 Auth Status
└── 📁 Test Data Setup
    └── 🔧 Manual User Verification (SQL)
```

**Legend:**
- 🟢 **Working** - Ready to test
- 🔄 **To Implement** - Requires production implementation
- 🔧 **Helper** - Database operations for testing

---

## 🚀 **Quick Start Commands**

### **Test Current Working APIs:**
```bash
# Health Check
curl http://localhost:8000/health

# Register User
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "postman@test.com", "password": "PostmanTest123!", "first_name": "Test", "last_name": "User"}'

# Manually activate user (PostgreSQL)
psql -d am_user_management -c "UPDATE user_accounts SET status = 'ACTIVE', verified_at = NOW() WHERE email = 'postman@test.com';"

# Login User
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "postman@test.com", "password": "PostmanTest123!"}'
```

This comprehensive testing guide covers all current APIs plus the production endpoints you can implement following the production guide! 🎯