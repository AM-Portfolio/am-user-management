"""Mock event bus for development"""
from typing import List, Dict, Any
from core.interfaces.event_bus import EventBus, DomainEvent


class MockEventBus(EventBus):
    """Mock event bus for development and testing"""
    
    def __init__(self):
        self.published_events: List[DomainEvent] = []
        self.subscribers: Dict[str, List[Any]] = {}
    
    async def publish(self, event: DomainEvent) -> None:
        """Mock publishing an event"""
        self.published_events.append(event)
        print(f"[MOCK EVENT BUS] Published event: {event.__class__.__name__}")
        print(f"[MOCK EVENT BUS] Event data: {event.__dict__}")
        
        # Call any registered handlers (for testing)
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                try:
                    if callable(handler):
                        await handler(event)
                    print(f"[MOCK EVENT BUS] Event handled by: {handler}")
                except Exception as e:
                    print(f"[MOCK EVENT BUS] Handler error: {e}")
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Mock publishing multiple events"""
        for event in events:
            await self.publish(event)
    
    async def subscribe(self, event_type: str, handler: Any) -> None:
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        print(f"[MOCK EVENT BUS] Subscribed to event: {event_type}")
    
    def get_published_events(self) -> List[DomainEvent]:
        """Get all published events (for testing)"""
        return self.published_events.copy()
    
    def get_subscribers(self) -> Dict[str, List[Any]]:
        """Get all subscribers (for testing)"""
        return self.subscribers.copy()
    
    def clear_published_events(self) -> None:
        """Clear published events (for testing)"""
        self.published_events.clear()
    
    def clear_subscribers(self) -> None:
        """Clear all subscribers (for testing)"""
        self.subscribers.clear()