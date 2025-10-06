"""Repository interface - Abstract base class for data persistence"""
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic, List
from uuid import UUID

from ..value_objects.user_id import UserId

T = TypeVar('T')


class Repository(ABC, Generic[T]):
    """Abstract base repository interface"""
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save an entity to the repository"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: UserId) -> Optional[T]:
        """Retrieve an entity by its ID"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: UserId) -> bool:
        """Delete an entity by its ID"""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: UserId) -> bool:
        """Check if an entity exists by its ID"""
        pass


class UserRepository(Repository[T]):
    """User-specific repository interface"""
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[T]:
        """Find user by email address"""
        pass
    
    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[T]:
        """Find user by phone number"""
        pass
    
    @abstractmethod
    async def list_active_users(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List active users with pagination"""
        pass