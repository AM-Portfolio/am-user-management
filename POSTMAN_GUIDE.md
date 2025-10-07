# User Management API - Postman Collection Guide

## Import Collection

1. Open Postman
2. Click **Import** button
3. Select `postman_collection.json` from this folder
4. Collection will appear in your sidebar

## Configure Environment

The collection uses port **8000** by default.

### Option 1: Use Default (localhost:8000)
- No configuration needed
- Works immediately for local testing

### Option 2: Use Replit URL
1. In Postman, click **Environments**
2. Create new environment or edit existing
3. Add variable:
   - Key: `USER_BASE`
   - Value: `https://your-replit-url.replit.dev:8000`

## Test Workflows

### Workflow A: User Registration & Login

**Step 1: Register User**
```
POST /api/v1/auth/register
Body: {
  "email": "test@example.com",
  "password": "securePassword123",
  "phone_number": "+1234567890"
}
```
Creates new user account

**Step 2: Login**
```
POST /api/v1/auth/login
Body: {
  "email": "test@example.com",
  "password": "securePassword123"
}
```
Returns user data for token creation

### Workflow B: OAuth2 Service Registration

**Step 1: Register Service**
```
POST /api/v1/service/register
```
Returns `consumer_key` and `consumer_secret`  
⚠️ **IMPORTANT:** Save these! Secret shown only once!

**Step 2: Validate Credentials**
```
POST /api/v1/service/validate-credentials
```
Verify your credentials work

**Step 3: Get Service Status**
```
GET /api/v1/service/{service_id}/status
Headers:
  X-Consumer-Key: {your_key}
  X-Consumer-Secret: {your_secret}
```

## All Endpoints

### Health & Info
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/api/v1/auth/status` | GET | Auth status |

### User Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | Authenticate user |

### OAuth2 Service Registration
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/service/register` | POST | Register OAuth2 service |
| `/api/v1/service/validate-credentials` | POST | Validate service credentials |
| `/api/v1/service/{id}/status` | GET | Get service status |
| `/api/v1/service/{id}/update` | PUT | Update service config |

### Internal APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/internal/v1/users/{id}` | GET | Get user by ID (internal) |
| `/docs` | GET | Interactive API docs |

## Automatic Environment Variables

The collection automatically saves:
- `user_id` - After registration/login
- `consumer_key` - After service registration
- `consumer_secret` - After service registration  
- `service_id` - After service registration

These are used in subsequent requests automatically!

## Common Issues

**422 Error:**
- Check request body matches expected fields
- Verify Content-Type is `application/json`

**Service registration fails:**
- Ensure `service_id` is unique
- All scope justifications must be provided

**Connection refused:**
- Service runs on port **8000**
- Verify service is running
