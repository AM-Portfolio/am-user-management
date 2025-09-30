"""Create user use case - Validates → saves → publishes UserCreated"""
from typing import Optional
from dataclasses import dataclass

from core.value_objects.email import Email
from core.value_objects.phone_number import PhoneNumber
from core.interfaces.repository import UserRepository
from core.interfaces.event_bus import EventBus
from ..services.password_hasher import PasswordHasherInterface
from ..services.email_service import EmailServiceInterface
from ...domain.models.user_account import UserAccount
from ...domain.exceptions.user_already_exists import EmailAlreadyExistsError, PhoneAlreadyExistsError


@dataclass
class CreateUserRequest:
    """Create user request data"""
    email: str
    password: str
    phone_number: Optional[str] = None


@dataclass
class CreateUserResponse:
    """Create user response data"""
    user_id: str
    email: str
    status: str
    created_at: str


class CreateUserUseCase:
    """Create user use case"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherInterface,
        email_service: EmailServiceInterface,
        event_bus: EventBus
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._email_service = email_service
        self._event_bus = event_bus
    
    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        """Execute create user use case"""
        # Validate input
        await self._validate_request(request)
        
        # Create value objects
        email = Email(request.email)
        phone_number = PhoneNumber(request.phone_number) if request.phone_number else None
        
        # Check if user already exists
        await self._check_user_exists(email, phone_number)
        
        # Hash password
        password_hash = self._password_hasher.hash_password(request.password)
        
        # Create user entity
        user = UserAccount.create(
            email=email,
            password_hash=password_hash,
            phone_number=phone_number
        )
        
        # Save user
        saved_user = await self._user_repository.save(user)
        
        # Send verification email
        await self._send_verification_email(saved_user)
        
        # Publish domain events
        await self._publish_events(saved_user)
        
        # Return response
        return CreateUserResponse(
            user_id=str(saved_user.id),
            email=str(saved_user.email),
            status=saved_user.status.value,
            created_at=saved_user.created_at.isoformat()
        )
    
    async def _validate_request(self, request: CreateUserRequest) -> None:
        """Validate create user request"""
        if not request.email:
            raise ValueError("Email is required")
        
        if not request.password:
            raise ValueError("Password is required")
        
        if len(request.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Additional password strength validation could be added here
    
    async def _check_user_exists(self, email: Email, phone_number: Optional[PhoneNumber]) -> None:
        """Check if user already exists"""
        # Check email
        existing_user = await self._user_repository.get_by_email(str(email))
        if existing_user:
            raise EmailAlreadyExistsError(str(email))
        
        # Check phone number if provided
        if phone_number:
            existing_user = await self._user_repository.get_by_phone(str(phone_number))
            if existing_user:
                raise PhoneAlreadyExistsError(str(phone_number))
    
    async def _send_verification_email(self, user: UserAccount) -> None:
        """Send email verification"""
        # In a real implementation, you would generate a verification token
        # and store it in a token repository
        verification_token = "mock_verification_token_" + str(user.id)
        
        try:
            await self._email_service.send_verification_email(
                to=user.email,
                token=verification_token
            )
        except Exception as e:
            # Log the error but don't fail user creation
            print(f"Failed to send verification email: {e}")
    
    async def _publish_events(self, user: UserAccount) -> None:
        """Publish domain events"""
        events = user.get_events()
        for event in events:
            await self._event_bus.publish(event)
        user.clear_events()