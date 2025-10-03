"""Integrated FastAPI application using the modular architecture"""
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# Import our infrastructure components
from shared_infra.database.config import db_config
from shared_infra.events.mock_event_bus import MockEventBus
from modules.account_management.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from modules.account_management.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from modules.account_management.infrastructure.services.mock_email_service import MockEmailService
from modules.account_management.application.use_cases.create_user import CreateUserUseCase, CreateUserRequest, CreateUserResponse
from modules.account_management.application.use_cases.login import LoginUseCase, LoginRequest, LoginResponse


# Dependency injection setup
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency"""
    async for session in db_config.get_session():
        yield session


async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyUserRepository:
    """Get user repository dependency"""
    return SQLAlchemyUserRepository(session)


def get_password_hasher() -> BcryptPasswordHasher:
    """Get password hasher dependency"""
    return BcryptPasswordHasher()


def get_email_service() -> MockEmailService:
    """Get email service dependency"""
    return MockEmailService()


def get_event_bus() -> MockEventBus:
    """Get event bus dependency"""
    return MockEventBus()


async def get_create_user_use_case(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher),
    email_service: MockEmailService = Depends(get_email_service),
    event_bus: MockEventBus = Depends(get_event_bus)
) -> CreateUserUseCase:
    """Get create user use case dependency"""
    return CreateUserUseCase(user_repository, password_hasher, email_service, event_bus)


async def get_login_use_case(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher),
    event_bus: MockEventBus = Depends(get_event_bus)
) -> LoginUseCase:
    """Get login use case dependency"""
    return LoginUseCase(user_repository, password_hasher, event_bus)


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    print("🚀 Starting AM User Management API...")
    
    # Create database tables
    try:
        await db_config.create_tables()
        print("✅ PostgreSQL database tables created successfully")
        print(f"📊 Database URL: {db_config.database_url}")
    except Exception as e:
        print(f"❌ Failed to create PostgreSQL database tables: {e}")
        print("💡 Make sure PostgreSQL is running: brew services start postgresql@15")
        print("� Make sure database exists: createdb am_user_management")
        raise e  # Don't fall back to SQLite, we want PostgreSQL
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AM User Management API...")
    await db_config.close()


# Create FastAPI app
app = FastAPI(
    title="AM User Management API",
    description="User management system with modular architecture and real database integration",
    version="0.2.0",
    debug=True,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests/responses
class RegisterRequest(BaseModel):
    """User registration request"""
    email: str
    password: str
    phone_number: Optional[str] = None


class LoginRequestModel(BaseModel):
    """User login request"""
    email: str
    password: str


# Health check endpoints
@app.get("/")
async def root():
    return {
        "message": "AM User Management API",
        "status": "running",
        "version": "0.2.0",
        "features": "Integrated with modular architecture and database"
    }


@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_db_session)):
    try:
        # Test database connection
        from sqlalchemy import text
        await session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "message": "Application and database are running successfully",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "degraded", 
            "message": "Application is running but database connection failed",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/api/v1/auth/status")
async def auth_status():
    return {
        "status": "Account management module fully integrated",
        "features": [
            "User registration with email verification",
            "User authentication with password hashing",
            "Domain events publishing",
            "Database persistence"
        ]
    }


# Real authentication endpoints using our use cases
@app.post("/api/v1/auth/register", response_model=CreateUserResponse)
async def register(
    request: RegisterRequest,
    create_user_use_case: CreateUserUseCase = Depends(get_create_user_use_case)
):
    """Register a new user"""
    try:
        # Convert API request to use case request
        use_case_request = CreateUserRequest(
            email=request.email,
            password=request.password,
            phone_number=request.phone_number
        )
        
        # Execute use case
        response = await create_user_use_case.execute(use_case_request)
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@app.post("/api/v1/auth/login")
async def login(
    request: LoginRequestModel,
    login_use_case: LoginUseCase = Depends(get_login_use_case)
):
    """Authenticate user and return JWT token"""
    import httpx
    import os
    
    try:
        # Convert API request to use case request
        use_case_request = LoginRequest(
            email=request.email,
            password=request.password
        )
        
        # Execute use case (authenticate user)
        auth_response = await login_use_case.execute(use_case_request)
        
        # Get JWT token from auth-tokens service
        # Use host.docker.internal to reach host from container
        auth_tokens_url = os.getenv('AUTH_TOKENS_URL', 'http://host.docker.internal:8080')
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                f"{auth_tokens_url}/api/v1/tokens/by-user-id",
                json={"user_id": auth_response.user_id},
                headers={"Content-Type": "application/json"}
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                
                # Return enhanced response with JWT token
                return {
                    "user_id": auth_response.user_id,
                    "email": auth_response.email,
                    "status": auth_response.status,
                    "session_id": auth_response.session_id,
                    "last_login_at": auth_response.last_login_at,
                    "requires_verification": auth_response.requires_verification,
                    # JWT token fields
                    "access_token": token_data.get("access_token"),
                    "token_type": token_data.get("token_type", "bearer"),
                    "expires_in": token_data.get("expires_in", 86400)
                }
            else:
                # Fallback to original response if token service fails
                print(f"Token service failed: {token_response.status_code}")
                return {
                    "user_id": auth_response.user_id,
                    "email": auth_response.email,
                    "status": auth_response.status,
                    "session_id": auth_response.session_id,
                    "last_login_at": auth_response.last_login_at,
                    "requires_verification": auth_response.requires_verification,
                    "access_token": None,
                    "token_type": "bearer",
                    "expires_in": 0,
                    "warning": "Token service unavailable"
                }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        if "invalid" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


# Internal API for auth-tokens service integration
@app.get("/internal/v1/users/{user_id}")
async def get_user_internal(
    user_id: str,
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository)
):
    """
    Internal endpoint for auth-tokens service to verify user status.
    Called when creating JWT tokens.
    """
    try:
        # Import UserId to create proper value object
        from core.value_objects.user_id import UserId
        
        # Create UserId object from string
        user_id_obj = UserId(user_id)
        
        # Look up user by user_id
        user = await user_repository.get_by_id(user_id_obj)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return user details for JWT token creation
        status_value = str(user.status.value).upper()  # Ensure uppercase comparison
        is_active = status_value == "ACTIVE"
        
        return {
            "user_id": str(user.id.value),  # Fixed: use user.id instead of user.user_id
            "username": user.email.value,  # Using email as username
            "email": user.email.value,
            "status": status_value,
            "scopes": ["read", "write"],  # Based on user roles/permissions
            "active": is_active
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )