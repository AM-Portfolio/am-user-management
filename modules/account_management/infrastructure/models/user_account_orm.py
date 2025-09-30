"""SQLAlchemy ORM model for UserAccount"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ...domain.enums.user_status import UserStatus

Base = declarative_base()


class UserAccountORM(Base):
    """SQLAlchemy ORM model for user account"""
    
    __tablename__ = "user_accounts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User credentials
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Status and verification
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Security fields
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserAccountORM(id={self.id}, email={self.email}, status={self.status})>"
    
    @classmethod
    def from_domain(cls, user_account) -> "UserAccountORM":
        """Create ORM instance from domain model"""
        return cls(
            id=user_account.id.value,
            email=str(user_account.email),
            password_hash=user_account.password_hash,
            status=user_account.status,
            phone_number=str(user_account.phone_number) if user_account.phone_number else None,
            created_at=user_account.created_at,
            updated_at=user_account.updated_at,
            verified_at=user_account.verified_at,
            last_login_at=user_account.last_login_at,
            failed_login_attempts=user_account.failed_login_attempts,
            locked_until=user_account.locked_until
        )
    
    def to_domain(self):
        """Convert ORM instance to domain model"""
        from core.value_objects.user_id import UserId
        from core.value_objects.email import Email
        from core.value_objects.phone_number import PhoneNumber
        from ...domain.models.user_account import UserAccount
        
        return UserAccount(
            id=UserId(str(self.id)),
            email=Email(self.email),
            password_hash=self.password_hash,
            status=self.status,
            phone_number=PhoneNumber(self.phone_number) if self.phone_number else None,
            created_at=self.created_at,
            updated_at=self.updated_at,
            verified_at=self.verified_at,
            last_login_at=self.last_login_at,
            failed_login_attempts=self.failed_login_attempts,
            locked_until=self.locked_until
        )