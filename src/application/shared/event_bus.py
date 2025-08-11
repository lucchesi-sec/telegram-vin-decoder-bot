"""Event bus for handling domain events."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, List

Event = TypeVar('Event')


class EventHandler(ABC, Generic[Event]):
    """Base class for event handlers."""
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle an event."""
        pass


class EventBus(ABC):
    """Interface for event bus."""
    
    @abstractmethod
    async def publish(self, event: Any) -> None:
        """Publish an event to be handled."""
        pass
    
    @abstractmethod
    async def publish_all(self, events: List[Any]) -> None:
        """Publish multiple events to be handled."""
        pass