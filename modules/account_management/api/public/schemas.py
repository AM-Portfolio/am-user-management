"""API schemas - CreateUserRequest, LoginResponse"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

from ...application.use_cases.create_user import CreateUserRequest as CreateUserUseCaseRequest
from ...application.use_cases.create_user import CreateUserResponse as CreateUserUseCaseResponse
from ...application.use_cases.login import LoginRequest as LoginUseCaseRequest
from ...application.use_cases.login import LoginResponse as LoginUseCaseResponse


class CreateUserRequest(BaseModel):
    """Create user API request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    phone_number: Optional[str] = Field(None, description="User phone number")
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
    
    def to_use_case_request(self) -> CreateUserUseCaseRequest:
        """Convert to use case request"""
        return CreateUserUseCaseRequest(
            email=self.email,
            password=self.password,
            phone_number=self.phone_number
        )


class CreateUserResponse(BaseModel):
    """Create user API response schema"""
    user_id: str = Field(..., description="Created user ID")
    email: str = Field(..., description="User email address")
    status: str = Field(..., description="User account status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    message: str = Field(default="User created successfully", description="Success message")
    
    @classmethod
    def from_use_case_response(cls, response: CreateUserUseCaseResponse) -> "CreateUserResponse":
        """Create from use case response"""
        return cls(
            user_id=response.user_id,
            email=response.email,
            status=response.status,
            created_at=datetime.fromisoformat(response.created_at),
            message="User created successfully. Please check your email for verification."
        )


class LoginRequest(BaseModel):
    """Login API request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    def to_use_case_request(self) -> LoginUseCaseRequest:
        """Convert to use case request"""
        return LoginUseCaseRequest(
            email=self.email,
            password=self.password
        )


class LoginResponse(BaseModel):
    """Login API response schema"""
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    status: str = Field(..., description="User account status")
    session_id: str = Field(..., description="Session identifier")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    requires_verification: bool = Field(default=False, description="Whether email verification is required")
    message: str = Field(default="Login successful", description="Success message")
    
    @classmethod
    def from_use_case_response(cls, response: LoginUseCaseResponse) -> "LoginResponse":
        """Create from use case response"""
        return cls(
            user_id=response.user_id,
            email=response.email,
            status=response.status,
            session_id=response.session_id,
            last_login_at=datetime.fromisoformat(response.last_login_at) if response.last_login_at else None,
            requires_verification=response.requires_verification,
            message="Login successful"
        )


class PasswordResetRequest(BaseModel):
    """Password reset API request schema"""
    email: EmailStr = Field(..., description="User email address")
    
    def to_use_case_request(self):
        """Convert to use case request - placeholder for now"""
        # TODO: Implement when ResetPasswordUseCase is created
        return {"email": self.email}


class PasswordResetResponse(BaseModel):
    """Password reset API response schema"""
    message: str = Field(..., description="Response message")
    email: str = Field(..., description="Email address")
    
    @classmethod
    def from_use_case_response(cls, response) -> "PasswordResetResponse":
        """Create from use case response - placeholder for now"""
        return cls(
            message="Password reset email sent successfully",
            email=response.get("email", "")
        )


class EmailVerificationRequest(BaseModel):
    """Email verification API request schema"""
    token: str = Field(..., description="Email verification token")


class EmailVerificationResponse(BaseModel):
    """Email verification API response schema"""
    message: str = Field(..., description="Verification result message")
    verified: bool = Field(..., description="Whether email was successfully verified")


class LogoutRequest(BaseModel):
    """Logout API request schema"""
    session_id: str = Field(..., description="Session ID to invalidate")


class LogoutResponse(BaseModel):
    """Logout API response schema"""
    message: str = Field(default="Logout successful", description="Logout confirmation message")


class ErrorResponse(BaseModel):
    """Generic error response schema"""
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
    field: Optional[str] = Field(None, description="Field that caused the error")
    details: Optional[dict] = Field(None, description="Additional error details")