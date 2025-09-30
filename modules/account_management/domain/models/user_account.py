"""User account domain entity"""
from datetime import datetime, timezone
from typing import Optional, List
from dataclasses import dataclass, field

from core.value_objects.user_id import UserId
from core.value_objects.email import Email
from core.value_objects.phone_number import PhoneNumber
from core.interfaces.event_bus import DomainEvent, UserCreatedEvent, UserEmailVerifiedEvent
from ..enums.user_status import UserStatus
from ..exceptions.invalid_credentials import InvalidPasswordError
from ..exceptions.email_not_verified import EmailNotVerifiedError


@dataclass
class UserAccount:
    """User account domain entity"""
    
    id: UserId
    email: Email
    password_hash: str
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    phone_number: Optional[PhoneNumber] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # Domain events
    _events: List[DomainEvent] = field(default_factory=list, init=False)
    
    @classmethod
    def create(
        cls,
        email: Email,
        password_hash: str,
        phone_number: Optional[PhoneNumber] = None
    ) -> "UserAccount":
        """Factory method to create a new user account"""
        user_id = UserId.generate()
        user = cls(
            id=user_id,
            email=email,
            password_hash=password_hash,
            phone_number=phone_number,
            status=UserStatus.PENDING_VERIFICATION
        )
        
        # Raise domain event
        user._add_event(UserCreatedEvent(
            user_id=user_id.value,
            email=str(email),
            phone=str(phone_number) if phone_number else None
        ))
        
        return user
    
    def verify_email(self) -> None:
        """Mark email as verified"""
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
            self.verified_at = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)
            
            # Raise domain event
            self._add_event(UserEmailVerifiedEvent(
                user_id=self.id.value,
                email=str(self.email)
            ))
    
    def is_email_verified(self) -> bool:
        """Check if email is verified"""
        return self.verified_at is not None
    
    def can_login(self) -> bool:
        """Check if user can log in"""
        if not self.status.can_login():
            return False
        
        if self.is_locked():
            return False
            
        return True
    
    def is_locked(self) -> bool:
        """Check if account is currently locked"""
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until
    
    def record_failed_login(self, max_attempts: int = 5, lockout_minutes: int = 15) -> None:
        """Record a failed login attempt"""
        self.failed_login_attempts += 1
        self.updated_at = datetime.now(timezone.utc)
        
        if self.failed_login_attempts >= max_attempts:
            self.locked_until = datetime.now(timezone.utc).replace(
                minute=datetime.now(timezone.utc).minute + lockout_minutes
            )
    
    def record_successful_login(self) -> None:
        """Record a successful login"""
        self.last_login_at = datetime.now(timezone.utc)
        self.failed_login_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self) -> None:
        """Deactivate user account"""
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.now(timezone.utc)
    
    def reactivate(self) -> None:
        """Reactivate user account"""
        if self.status == UserStatus.INACTIVE:
            self.status = UserStatus.ACTIVE if self.is_email_verified() else UserStatus.PENDING_VERIFICATION
            self.updated_at = datetime.now(timezone.utc)
    
    def update_email(self, new_email: Email) -> None:
        """Update email and reset verification status"""
        if new_email != self.email:
            self.email = new_email
            self.status = UserStatus.PENDING_VERIFICATION
            self.verified_at = None
            self.updated_at = datetime.now(timezone.utc)
    
    def update_password(self, new_password_hash: str) -> None:
        """Update password hash"""
        self.password_hash = new_password_hash
        self.updated_at = datetime.now(timezone.utc)
    
    def _add_event(self, event: DomainEvent) -> None:
        """Add a domain event"""
        self._events.append(event)
    
    def get_events(self) -> List[DomainEvent]:
        """Get all domain events"""
        return self._events.copy()
    
    def clear_events(self) -> None:
        """Clear all domain events"""
        self._events.clear()