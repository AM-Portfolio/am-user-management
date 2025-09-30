"""Event bus interface - Abstract event publishing"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    """Base domain event class"""
    event_id: UUID
    aggregate_id: UUID
    event_type: str
    occurred_at: datetime
    version: int
    data: Dict[str, Any]
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = uuid4()
        if not self.occurred_at:
            self.occurred_at = datetime.utcnow()


@dataclass
class UserCreatedEvent(DomainEvent):
    """User created domain event"""
    
    def __init__(self, user_id: UUID, email: str, **kwargs):
        super().__init__(
            event_id=uuid4(),
            aggregate_id=user_id,
            event_type="user.created",
            occurred_at=datetime.utcnow(),
            version=1,
            data={
                "user_id": str(user_id),
                "email": email,
                **kwargs
            }
        )


@dataclass
class UserEmailVerifiedEvent(DomainEvent):
    """User email verified domain event"""
    
    def __init__(self, user_id: UUID, email: str, **kwargs):
        super().__init__(
            event_id=uuid4(),
            aggregate_id=user_id,
            event_type="user.email_verified",
            occurred_at=datetime.utcnow(),
            version=1,
            data={
                "user_id": str(user_id),
                "email": email,
                **kwargs
            }
        )


class EventBus(ABC):
    """Abstract event bus for publishing domain events"""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event"""
        pass
    
    @abstractmethod
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple domain events"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: Any) -> None:
        """Subscribe to an event type"""
        pass