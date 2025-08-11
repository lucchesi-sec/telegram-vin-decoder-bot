"""Simple event bus implementation."""

import logging
from typing import Dict, Type, Any, List
from src.application.shared.event_bus import EventBus, EventHandler

logger = logging.getLogger(__name__)


class SimpleEventBus(EventBus):
    """Simple implementation of event bus."""
    
    def __init__(self):
        self.handlers: Dict[Type, List[EventHandler]] = {}
    
    def register_handler(self, event_type: Type, handler: EventHandler) -> None:
        """Register a handler for an event type.
        
        Args:
            event_type: The event type
            handler: The handler instance
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.debug(f"Registered handler for {event_type}")
    
    async def publish(self, event: Any) -> None:
        """Publish an event to be handled.
        
        Args:
            event: The event to publish
        """
        event_type = type(event)
        handlers = self.handlers.get(event_type, [])
        
        logger.debug(f"Publishing event: {event_type} to {len(handlers)} handlers")
        
        for handler in handlers:
            try:
                await handler.handle(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    async def publish_all(self, events: List[Any]) -> None:
        """Publish multiple events to be handled.
        
        Args:
            events: The events to publish
        """
        for event in events:
            await self.publish(event)