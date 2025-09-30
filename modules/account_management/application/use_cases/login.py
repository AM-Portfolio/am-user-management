"""Login use case - Authenticates → returns session_id (token handled externally)"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

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
    session_id: str
    last_login_at: str
    requires_verification: bool = False


class LoginUseCase:
    """Login use case"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherInterface,
        require_email_verification: bool = True
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._require_email_verification = require_email_verification
    
    async def execute(self, request: LoginRequest) -> LoginResponse:
        """Execute login use case"""
        # Validate input
        self._validate_request(request)
        
        # Create email value object
        email = Email(request.email)
        
        # Find user by email
        user = await self._get_user_by_email(email)
        
        # Check if account is locked
        if user.is_locked():
            raise AccountLockedError("Account is temporarily locked due to too many failed login attempts")
        
        # Verify password
        if not self._password_hasher.verify_password(request.password, user.password_hash):
            # Record failed attempt
            user.record_failed_login()
            await self._user_repository.save(user)
            raise InvalidPasswordError("Invalid password")
        
        # Check if user can login
        if not user.can_login():
            raise InvalidCredentialsError(f"Account status does not allow login: {user.status.value}")
        
        # Check email verification if required
        if self._require_email_verification and not user.is_email_verified():
            raise EmailNotVerifiedError(str(user.email))
        
        # Record successful login
        user.record_successful_login()
        await self._user_repository.save(user)
        
        # Generate session ID (in real implementation, this would be handled by auth service)
        session_id = f"session_{user.id}_{int(datetime.now().timestamp())}"
        
        # Return response
        return LoginResponse(
            user_id=str(user.id),
            email=str(user.email),
            status=user.status.value,
            session_id=session_id,
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else "",
            requires_verification=not user.is_email_verified()
        )
    
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