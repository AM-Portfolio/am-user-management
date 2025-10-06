"""Reset password use case - Sends reset link via email"""
from typing import Optional
from dataclasses import dataclass

from core.value_objects.email import Email
from core.interfaces.repository import UserRepository
from ..services.email_service import EmailServiceInterface
from ...domain.models.user_account import UserAccount


@dataclass
class ResetPasswordRequest:
    """Reset password request data"""
    email: str


@dataclass
class ResetPasswordResponse:
    """Reset password response data"""
    email: str
    message: str


class ResetPasswordUseCase:
    """Reset password use case"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailServiceInterface
    ):
        self._user_repository = user_repository
        self._email_service = email_service
    
    async def execute(self, request: ResetPasswordRequest) -> ResetPasswordResponse:
        """Execute reset password use case"""
        # Validate input
        if not request.email:
            raise ValueError("Email is required")
        
        # Create email value object
        email = Email(request.email)
        
        # Find user by email (don't reveal if user exists or not for security)
        user = await self._user_repository.get_by_email(str(email))
        
        if user:
            # Generate reset token (in real implementation, store in token repository)
            reset_token = "mock_reset_token_" + str(user.id)
            
            # Send reset email
            await self._email_service.send_password_reset_email(
                to=user.email,
                token=reset_token
            )
        
        # Always return success message for security
        return ResetPasswordResponse(
            email=str(email),
            message="If an account with that email exists, a password reset link has been sent."
        )