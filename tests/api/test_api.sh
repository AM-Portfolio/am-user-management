#!/bin/bash

echo "🚀 Testing AM User Management API"
echo "=================================="

echo ""
echo "1. Testing Root Endpoint:"
curl -s http://localhost:8000/ | python3 -m json.tool

echo ""
echo "2. Testing Health Check:"
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "3. Testing Auth Status:"
curl -s http://localhost:8000/api/v1/auth/status | python3 -m json.tool

echo ""
echo "4. Testing Register Placeholder:"
curl -s -X POST http://localhost:8000/api/v1/auth/register | python3 -m json.tool

echo ""
echo "5. Testing Login Placeholder:"
curl -s -X POST http://localhost:8000/api/v1/auth/login | python3 -m json.tool

echo ""
echo "✅ API Testing Complete!"
echo ""
echo "📖 For interactive testing, visit:"
echo "   - http://localhost:8000/docs (Swagger UI)"
echo "   - http://localhost:8000/redoc (ReDoc)"