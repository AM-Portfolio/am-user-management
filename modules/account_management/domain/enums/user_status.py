"""User status enumeration"""
from enum import Enum


class UserStatus(str, Enum):
    """User account status enumeration"""
    
    ACTIVE = "active"
    INACTIVE = "inactive"  
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    
    def is_active(self) -> bool:
        """Check if user is in active state"""
        return self == UserStatus.ACTIVE
    
    def can_login(self) -> bool:
        """Check if user can log in"""
        return self in (UserStatus.ACTIVE,)
    
    def requires_verification(self) -> bool:
        """Check if user needs email verification"""
        return self == UserStatus.PENDING_VERIFICATION