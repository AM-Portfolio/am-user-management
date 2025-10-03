"""Comprehensive test script for integrated FastAPI application"""
import asyncio
import json
import requests
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def make_request(method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Make HTTP request and return JSON response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "success": 200 <= response.status_code < 300
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "success": False}


def print_test_result(test_name: str, result: Dict[Any, Any]):
    """Print formatted test result"""
    print(f"\n🧪 {test_name}")
    print("=" * 50)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    status = "✅ PASSED" if result["success"] else "❌ FAILED"
    print(f"{status} - Status Code: {result['status_code']}")
    print(f"Response: {json.dumps(result['response'], indent=2)}")


def main():
    """Run comprehensive API tests"""
    print("🚀 Starting comprehensive API tests for integrated application...")
    print(f"Base URL: {BASE_URL}")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Test 1: Root endpoint
    result = make_request("GET", "/")
    print_test_result("Root Endpoint", result)
    
    # Test 2: Health check
    result = make_request("GET", "/health")
    print_test_result("Health Check", result)
    
    # Test 3: Auth status
    result = make_request("GET", "/api/v1/auth/status")
    print_test_result("Auth Status", result)
    
    # Test 4: User registration (success case)
    test_user_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "phone_number": "+1234567890"
    }
    result = make_request("POST", "/api/v1/auth/register", test_user_data)
    print_test_result("User Registration (New User)", result)
    
    # Test 5: User registration (duplicate email - should fail)
    result = make_request("POST", "/api/v1/auth/register", test_user_data)
    print_test_result("User Registration (Duplicate Email)", result)
    
    # Test 6: User registration (invalid email)
    invalid_user_data = {
        "email": "not-an-email",
        "password": "SecurePassword123!",
        "phone_number": "+1234567890"
    }
    result = make_request("POST", "/api/v1/auth/register", invalid_user_data)
    print_test_result("User Registration (Invalid Email)", result)
    
    # Test 7: User registration (weak password)
    weak_password_data = {
        "email": "test2@example.com",
        "password": "123",
        "phone_number": "+1234567891"
    }
    result = make_request("POST", "/api/v1/auth/register", weak_password_data)
    print_test_result("User Registration (Weak Password)", result)
    
    # Test 8: User login (success case)
    login_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }
    result = make_request("POST", "/api/v1/auth/login", login_data)
    print_test_result("User Login (Valid Credentials)", result)
    
    # Test 9: User login (invalid password)
    invalid_login_data = {
        "email": "test@example.com",
        "password": "WrongPassword"
    }
    result = make_request("POST", "/api/v1/auth/login", invalid_login_data)
    print_test_result("User Login (Invalid Password)", result)
    
    # Test 10: User login (non-existent user)
    nonexistent_login_data = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!"
    }
    result = make_request("POST", "/api/v1/auth/login", nonexistent_login_data)
    print_test_result("User Login (Non-existent User)", result)
    
    # Test 11: Register user without phone number
    no_phone_data = {
        "email": "nophone@example.com",
        "password": "SecurePassword123!"
    }
    result = make_request("POST", "/api/v1/auth/register", no_phone_data)
    print_test_result("User Registration (No Phone Number)", result)
    
    print("\n" + "="*60)
    print("🎉 Comprehensive API testing completed!")
    print("="*60)


if __name__ == "__main__":
    main()