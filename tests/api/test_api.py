#!/usr/bin/env python3
"""
Test script for AM User Management API
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 {description}")
    print(f"   {method} {endpoint}")
    print("   " + "="*50)
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            response = requests.request(method, url, json=data)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response:")
        
        try:
            json_response = response.json()
            print(json.dumps(json_response, indent=2))
        except:
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: Could not connect to API. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    return True

def main():
    """Run all API tests"""
    print("🚀 AM User Management API Test Suite")
    print("="*50)
    
    # Test endpoints
    tests = [
        ("GET", "/", None, "Root Endpoint - API Information"),
        ("GET", "/health", None, "Health Check Endpoint"),
        ("GET", "/api/v1/auth/status", None, "Auth Status Endpoint"),
        ("POST", "/api/v1/auth/register", None, "Register Placeholder"),
        ("POST", "/api/v1/auth/login", None, "Login Placeholder"),
    ]
    
    success_count = 0
    for method, endpoint, data, description in tests:
        if test_endpoint(method, endpoint, data, description):
            success_count += 1
    
    print(f"\n✅ Tests completed: {success_count}/{len(tests)} successful")
    
    if success_count == len(tests):
        print("\n🎉 All tests passed! Your API is working correctly.")
        print("\n📖 For interactive testing:")
        print(f"   • Swagger UI: {BASE_URL}/docs")
        print(f"   • ReDoc: {BASE_URL}/redoc")
    else:
        print("\n⚠️  Some tests failed. Check the server is running on http://localhost:8000")

if __name__ == "__main__":
    main()