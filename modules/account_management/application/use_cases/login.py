"""Login use case - Authenticates → returns session_id (token handled externally)"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import httpx
import os

from core.value_objects.email import Email
from core.interfaces.repository import UserRepository
from ..services.password_hasher import PasswordHasherInterface
from ...domain.models.user_account import UserAccount
from ...domain.exceptions.invalid_credentials import (
    InvalidCredentialsError, 
    AccountLockedError,
    InvalidPasswordError,
    InvalidEmailError
)
from ...domain.exceptions.email_not_verified import EmailNotVerifiedError


@dataclass
class LoginRequest:
    """Login request data"""
    email: str
    password: str


@dataclass
class LoginResponse:
    """Login response data"""
    user_id: str
    email: str
    status: str
    scopes: list
    access_token: str


class LoginUseCase:
    """Login use case"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherInterface,
        event_bus,
        require_email_verification: bool = True
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._event_bus = event_bus
        self._require_email_verification = require_email_verification
    
    async def execute(self, request: LoginRequest) -> LoginResponse:
        """Execute login use case"""
        try:
            logging.info(f"Login attempt for email: {request.email}")
            
            # Validate input
            self._validate_request(request)
            
            # Create email value object
            email = Email(request.email)
            
            # Find user by email
            user = await self._get_user_by_email(email)
            logging.info(f"Found user with email: {user.email}, status: {user.status.value}")
            
            # Check if account is locked
            if user.is_locked():
                raise AccountLockedError("Account is temporarily locked due to too many failed login attempts")
            
            # Verify password
            logging.info(f"Verifying password for user: {user.email}")
            if not self._password_hasher.verify_password(request.password, user.password_hash):
                # Record failed attempt
                user.record_failed_login()
                await self._user_repository.save(user)
                raise InvalidPasswordError("Invalid password")
            
            logging.info(f"Password verified successfully for user: {user.email}")
            
            # Check if user can login
            if not user.can_login():
                raise InvalidCredentialsError(f"Account status does not allow login: {user.status.value}")
            
            # Check email verification if required
            if self._require_email_verification and not user.is_email_verified():
                raise EmailNotVerifiedError(str(user.email))
            
            # Record successful login
            user.record_successful_login()
            await self._user_repository.save(user)
            
            # Get user scopes (default scopes for now)
            scopes = ["read", "write"]
            
            # Call Auth Tokens service to get JWT token using validated user_id
            access_token = await self._get_access_token(str(user.id))
            
            # Return response
            return LoginResponse(
                user_id=str(user.id),
                email=str(user.email),
                status=user.status.value,
                scopes=scopes,
                access_token=access_token
            )
        except Exception as e:
            logging.error(f"Error in login use case: {str(e)}", exc_info=True)
            raise
    
    def _validate_request(self, request: LoginRequest) -> None:
        """Validate login request"""
        if not request.email:
            raise ValueError("Email is required")
        
        if not request.password:
            raise ValueError("Password is required")
    
    async def _get_user_by_email(self, email: Email) -> UserAccount:
        """Get user by email"""
        user = await self._user_repository.get_by_email(str(email))
        if not user:
            raise InvalidEmailError(str(email))
        return user
    
    async def _get_access_token(self, user_id: str) -> str:
        """Call Auth Tokens service to get JWT access token using validated user_id"""
        auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8080")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{auth_service_url}/api/v1/tokens/by-user-id",
                    json={"user_id": user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logging.info(f"Auth Tokens response: {data}")
                    access_token = data.get("access_token")
                    if not access_token:
                        logging.error(f"Auth service returned invalid response - missing access_token: {data}")
                        raise InvalidCredentialsError("Failed to generate access token - invalid response from auth service")
                    return access_token
                else:
                    logging.error(f"Auth service error: {response.status_code} - {response.text}")
                    raise InvalidCredentialsError("Failed to generate access token")
        except httpx.RequestError as e:
            logging.error(f"Failed to connect to auth service: {str(e)}")
            raise InvalidCredentialsError("Authentication service unavailable")


@dataclass
class LogoutRequest:
    """Logout request data"""
    session_id: str


class LogoutUseCase:
    """Logout use case"""
    
    def __init__(self):
        pass  # In real implementation, would have session repository
    
    async def execute(self, request: LogoutRequest) -> bool:
        """Execute logout use case"""
        # In real implementation, would invalidate session in auth service
        # For now, just return success
        return True