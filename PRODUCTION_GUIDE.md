# 🚀 Production Implementation Guide - AM User Management

This guide provides comprehensive instructions for implementing production-ready features for the AM User Management system, particularly focusing on email verification, security, and scalability considerations.

## 📋 Table of Contents

1. [Email Verification System](#email-verification-system)
2. [Security Enhancements](#security-enhancements)
3. [Performance Optimizations](#performance-optimizations)
4. [Monitoring & Logging](#monitoring--logging)
5. [Deployment Considerations](#deployment-considerations)
6. [API Documentation](#api-documentation)

---

## 🔐 Email Verification System

### 1. Email Verification Tokens

#### Implementation Steps

**Step 1: Create Email Verification Token Value Object**

```python
# core/value_objects/verification_token.py
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

@dataclass(frozen=True)
class VerificationToken:
    """Email verification token value object"""
    
    token: str
    expires_at: datetime
    
    @classmethod
    def generate(cls, expiry_hours: int = 24) -> "VerificationToken":
        """Generate a new verification token"""
        # Generate cryptographically secure random token
        raw_token = secrets.token_urlsafe(32)
        
        # Create expiry timestamp
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        
        return cls(token=raw_token, expires_at=expires_at)
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def hash_token(self) -> str:
        """Generate hash of token for database storage"""
        return hashlib.sha256(self.token.encode()).hexdigest()
```

**Step 2: Add Email Verification Fields to User Domain Model**

```python
# modules/account_management/domain/models/user_account.py
@dataclass
class UserAccount:
    # ... existing fields ...
    email_verification_token: Optional[str] = None  # Store hashed token
    email_verification_expires: Optional[datetime] = None
    
    def generate_email_verification_token(self, expiry_hours: int = 24) -> str:
        """Generate email verification token"""
        token = VerificationToken.generate(expiry_hours)
        self.email_verification_token = token.hash_token()
        self.email_verification_expires = token.expires_at
        self.updated_at = datetime.now(timezone.utc)
        return token.token  # Return raw token for email
    
    def verify_email_with_token(self, token: str) -> bool:
        """Verify email using token"""
        if not self.email_verification_token or not self.email_verification_expires:
            return False
        
        # Check if token is expired
        if datetime.now(timezone.utc) > self.email_verification_expires:
            return False
        
        # Verify token hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if token_hash != self.email_verification_token:
            return False
        
        # Mark as verified
        self.verify_email()
        self.email_verification_token = None
        self.email_verification_expires = None
        return True
```

**Step 3: Update Database Schema**

```python
# modules/account_management/infrastructure/models/user_account_orm.py
class UserAccountORM(Base):
    # ... existing fields ...
    email_verification_token = Column(String(64), nullable=True, index=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
```

**Step 4: Create Email Verification Use Case**

```python
# modules/account_management/application/use_cases/verify_email.py
from dataclasses import dataclass
from core.interfaces.repository import UserRepository
from ...domain.exceptions.invalid_credentials import InvalidEmailError
from ...domain.exceptions.email_verification import (
    InvalidTokenError, 
    TokenExpiredError
)

@dataclass
class VerifyEmailRequest:
    token: str

@dataclass
class VerifyEmailResponse:
    user_id: str
    email: str
    verified_at: str
    success: bool

class VerifyEmailUseCase:
    def __init__(self, user_repository: UserRepository, event_bus):
        self._user_repository = user_repository
        self._event_bus = event_bus
    
    async def execute(self, request: VerifyEmailRequest) -> VerifyEmailResponse:
        """Verify user email with token"""
        # Find user by token (you'll need to add this method to repository)
        user = await self._user_repository.get_by_verification_token(request.token)
        
        if not user:
            raise InvalidTokenError("Invalid or expired verification token")
        
        # Verify the token
        if not user.verify_email_with_token(request.token):
            if user.email_verification_expires and datetime.now(timezone.utc) > user.email_verification_expires:
                raise TokenExpiredError("Verification token has expired")
            raise InvalidTokenError("Invalid verification token")
        
        # Save updated user
        await self._user_repository.save(user)
        
        return VerifyEmailResponse(
            user_id=str(user.id),
            email=str(user.email),
            verified_at=user.verified_at.isoformat(),
            success=True
        )
```

### 2. Email Service Implementation

**Step 1: Create Email Templates**

```python
# shared_infra/email/templates/verification_email.py
def get_verification_email_template(user_name: str, verification_link: str) -> dict:
    """Get email verification template"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{ max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .button {{ 
                background-color: #4CAF50; 
                color: white; 
                padding: 12px 24px; 
                text-decoration: none; 
                border-radius: 4px; 
                display: inline-block; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to AM User Management!</h1>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>
                <p>Thank you for registering with AM User Management. Please verify your email address by clicking the button below:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                </p>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all;">{verification_link}</p>
                <p><strong>This link will expire in 24 hours.</strong></p>
                <p>If you didn't create this account, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to AM User Management!
    
    Hi {user_name},
    
    Thank you for registering with AM User Management. 
    Please verify your email address by visiting this link:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create this account, please ignore this email.
    """
    
    return {
        "subject": "Verify your AM User Management account",
        "html_body": html_content,
        "text_body": text_content
    }
```

**Step 2: Implement Production Email Service**

```python
# shared_infra/email/services/smtp_email_service.py
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from typing import List, Optional

class SMTPEmailService:
    """Production SMTP email service"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        from_email: str,
        from_name: str = "AM User Management",
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name
        self.use_tls = use_tls
        self.logger = logging.getLogger(__name__)
    
    async def send_verification_email(
        self, 
        to_email: str, 
        user_name: str, 
        verification_token: str,
        base_url: str
    ) -> bool:
        """Send email verification email"""
        try:
            # Create verification link
            verification_link = f"{base_url}/verify-email?token={verification_token}"
            
            # Get email template
            from ..templates.verification_email import get_verification_email_template
            template = get_verification_email_template(user_name, verification_link)
            
            # Send email
            return await self._send_email(
                to_email=to_email,
                subject=template["subject"],
                html_body=template["html_body"],
                text_body=template["text_body"]
            )
        except Exception as e:
            self.logger.error(f"Failed to send verification email to {to_email}: {str(e)}")
            return False
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text and HTML parts
            text_part = MIMEText(text_body, "plain")
            html_part = MIMEText(html_body, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    self._add_attachment(message, file_path)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
```

**Step 3: Configure Email Settings**

```python
# shared_infra/config/email_settings.py
from pydantic import BaseSettings, EmailStr
from typing import Optional

class EmailSettings(BaseSettings):
    """Email configuration settings"""
    
    # SMTP Configuration
    SMTP_SERVER: str = "smtp.gmail.com"  # or your SMTP server
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_USE_TLS: bool = True
    
    # Email Details
    FROM_EMAIL: EmailStr
    FROM_NAME: str = "AM User Management"
    
    # Application URLs
    BASE_URL: str = "http://localhost:8000"  # Change for production
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Usage in dependency injection
email_settings = EmailSettings()
```

### 3. API Endpoints

**Step 1: Email Verification Endpoint**

```python
# modules/account_management/api/public/auth_router.py

@router.get(
    "/verify-email",
    summary="Verify email address",
    description="Verify user email with verification token"
)
@require_module("account_management")
async def verify_email(
    token: str,
    verify_email_use_case: Annotated[VerifyEmailUseCase, Depends()]
):
    """Verify user email"""
    try:
        request = VerifyEmailRequest(token=token)
        result = await verify_email_use_case.execute(request)
        
        return {
            "message": "Email verified successfully",
            "user_id": result.user_id,
            "verified_at": result.verified_at
        }
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": str(e),
                "type": "invalid_token"
            }
        )
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "message": str(e),
                "type": "token_expired"
            }
        )

@router.post(
    "/resend-verification",
    summary="Resend verification email",
    description="Resend email verification link"
)
@require_module("account_management")
async def resend_verification_email(
    request: ResendVerificationRequest,
    resend_verification_use_case: Annotated[ResendVerificationUseCase, Depends()]
):
    """Resend verification email"""
    try:
        result = await resend_verification_use_case.execute(request)
        return {
            "message": "Verification email sent successfully",
            "email": result.email
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### 4. Frontend Integration

**Step 1: Email Verification Page (React Example)**

```jsx
// components/EmailVerification.jsx
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const EmailVerification = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('verifying'); // verifying, success, error
    const [message, setMessage] = useState('Verifying your email...');

    useEffect(() => {
        const verifyEmail = async () => {
            try {
                const response = await fetch(`/api/v1/auth/verify-email?token=${token}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    setStatus('success');
                    setMessage('Email verified successfully! You can now log in.');
                    setTimeout(() => navigate('/login'), 3000);
                } else {
                    const error = await response.json();
                    setStatus('error');
                    setMessage(error.detail.message || 'Verification failed');
                }
            } catch (error) {
                setStatus('error');
                setMessage('Network error occurred during verification');
            }
        };

        if (token) {
            verifyEmail();
        }
    }, [token, navigate]);

    return (
        <div className="verification-container">
            <div className="verification-card">
                {status === 'verifying' && (
                    <div className="spinner">Loading...</div>
                )}
                
                {status === 'success' && (
                    <div className="success-icon">✅</div>
                )}
                
                {status === 'error' && (
                    <div className="error-icon">❌</div>
                )}
                
                <h2>Email Verification</h2>
                <p>{message}</p>
                
                {status === 'error' && (
                    <button onClick={() => navigate('/resend-verification')}>
                        Resend Verification Email
                    </button>
                )}
            </div>
        </div>
    );
};

export default EmailVerification;
```

---

## 🔒 Security Enhancements

### 1. Rate Limiting

```python
# shared_infra/security/rate_limiter.py
import redis
from datetime import timedelta
from typing import Optional

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def check_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: timedelta
    ) -> tuple[bool, int, int]:
        """
        Check if rate limit is exceeded
        Returns: (is_allowed, current_count, remaining_count)
        """
        current = await self.redis.get(key)
        
        if current is None:
            await self.redis.setex(key, window, 1)
            return True, 1, limit - 1
        
        current_count = int(current)
        if current_count >= limit:
            return False, current_count, 0
        
        await self.redis.incr(key)
        return True, current_count + 1, limit - current_count - 1

# Usage in FastAPI middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/v1/auth"):
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}:{request.url.path}"
        
        allowed, current, remaining = await rate_limiter.check_rate_limit(
            key, limit=10, window=timedelta(minutes=1)
        )
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
    
    response = await call_next(request)
    return response
```

### 2. Password Security

```python
# modules/account_management/domain/value_objects/password_policy.py
import re
from dataclasses import dataclass
from typing import List

@dataclass
class PasswordPolicy:
    """Password policy enforcement"""
    
    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    forbidden_patterns: List[str] = None
    
    def validate(self, password: str) -> tuple[bool, List[str]]:
        """Validate password against policy"""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check forbidden patterns (common passwords, patterns)
        if self.forbidden_patterns:
            for pattern in self.forbidden_patterns:
                if pattern.lower() in password.lower():
                    errors.append("Password contains forbidden pattern")
                    break
        
        return len(errors) == 0, errors
```

### 3. JWT Token Management

```python
# shared_infra/security/jwt_service.py
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

class JWTService:
    def __init__(
        self, 
        secret_key: str, 
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(self, user_id: str, email: str) -> str:
        """Create JWT access token"""
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[Any, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

---

## ⚡ Performance Optimizations

### 1. Database Connection Pooling

```python
# shared_infra/database/config_production.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool

class ProductionDatabaseConfig:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,          # Number of connections to maintain
            max_overflow=30,       # Additional connections allowed
            pool_pre_ping=True,    # Validate connections before use
            pool_recycle=3600,     # Recycle connections every hour
            echo=False             # Set to True for SQL debugging
        )
```

### 2. Caching Strategy

```python
# shared_infra/cache/redis_cache.py
import redis.asyncio as redis
import json
from typing import Optional, Any
from datetime import timedelta

class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[timedelta] = None
    ) -> bool:
        """Set cached value"""
        try:
            serialized = json.dumps(value)
            if expire:
                await self.redis.setex(key, expire, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False
```

---

## 📊 Monitoring & Logging

### 1. Application Monitoring

```python
# shared_infra/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')
LOGIN_ATTEMPTS = Counter('login_attempts_total', 'Login attempts', ['status'])

def monitor_requests(func):
    """Decorator to monitor API requests"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(method='POST', endpoint=func.__name__, status='success').inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method='POST', endpoint=func.__name__, status='error').inc()
            raise
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    return wrapper
```

### 2. Structured Logging

```python
# shared_infra/logging/logger_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logging():
    """Configure application logging"""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
```

---

## 🚀 Deployment Considerations

### 1. Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main_integrated:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/am_user_management
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    deploy:
      replicas: 3

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: am_user_management
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

### 3. Environment Variables

```bash
# .env.production
# Database
DATABASE_URL=postgresql+asyncpg://user:secure_password@localhost:5432/am_user_management
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://localhost:6379
REDIS_POOL_SIZE=10

# JWT
JWT_SECRET_KEY=your-super-secure-secret-key-at-least-32-characters-long
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=AM User Management

# Application
BASE_URL=https://yourdomain.com
DEBUG=false
LOG_LEVEL=INFO

# Security
BCRYPT_ROUNDS=12
RATE_LIMIT_PER_MINUTE=60
MAX_LOGIN_ATTEMPTS=5
```

---

## 📚 API Documentation

### 1. OpenAPI Schema Enhancement

```python
# Add to main_integrated.py
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AM User Management API",
        version="1.0.0",
        description="""
        A comprehensive user management system with email verification,
        authentication, and role-based access control.
        
        ## Authentication
        This API uses JWT tokens for authentication. After login, include the
        access token in the Authorization header: `Bearer <token>`
        
        ## Rate Limiting
        API endpoints are rate-limited to prevent abuse. Standard limits:
        - Authentication endpoints: 10 requests per minute
        - General endpoints: 60 requests per minute
        
        ## Email Verification
        New users must verify their email address before logging in.
        A verification email is sent automatically upon registration.
        """,
        routes=app.routes,
        servers=[
            {"url": "https://api.yourdomain.com", "description": "Production server"},
            {"url": "https://staging-api.yourdomain.com", "description": "Staging server"},
            {"url": "http://localhost:8000", "description": "Development server"}
        ]
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from login endpoint"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

## 🔧 Implementation Checklist

### Phase 1: Core Email Verification
- [ ] Create verification token value object
- [ ] Update user domain model with token fields
- [ ] Update database schema with migration
- [ ] Implement verification use cases
- [ ] Create email templates
- [ ] Add verification API endpoints

### Phase 2: Email Service Integration
- [ ] Choose email provider (SendGrid, AWS SES, etc.)
- [ ] Implement production email service
- [ ] Configure SMTP settings
- [ ] Test email delivery
- [ ] Add email monitoring

### Phase 3: Security Enhancements
- [ ] Implement rate limiting
- [ ] Add password policy enforcement
- [ ] Set up JWT token management
- [ ] Add request validation
- [ ] Implement CORS properly

### Phase 4: Performance & Monitoring
- [ ] Configure database connection pooling
- [ ] Implement caching strategy
- [ ] Add application metrics
- [ ] Set up structured logging
- [ ] Configure health checks

### Phase 5: Deployment
- [ ] Create Docker containers
- [ ] Set up container orchestration
- [ ] Configure load balancer
- [ ] Set up SSL certificates
- [ ] Configure environment variables
- [ ] Set up CI/CD pipeline

---

## 🚨 Security Best Practices

1. **Always use HTTPS** in production
2. **Store secrets securely** (use environment variables, not code)
3. **Implement proper CORS** policies
4. **Use rate limiting** on all public endpoints
5. **Validate all inputs** on both client and server side
6. **Hash passwords** with a strong algorithm (bcrypt with 12+ rounds)
7. **Implement proper session management** with JWT tokens
8. **Log security events** for monitoring and debugging
9. **Keep dependencies updated** and scan for vulnerabilities
10. **Use database migrations** for schema changes

---

This production guide provides a comprehensive roadmap for implementing a robust, scalable user management system. Each section includes practical code examples and configuration that you can adapt to your specific requirements.

For questions or support, refer to the project documentation or open an issue in the repository.