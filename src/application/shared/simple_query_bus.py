"""Simple query bus implementation."""

import logging
from typing import Dict, Type, Any
from src.application.shared.query_bus import QueryBus, QueryHandler

logger = logging.getLogger(__name__)


class SimpleQueryBus(QueryBus):
    """Simple implementation of query bus."""
    
    def __init__(self):
        self.handlers: Dict[Type, QueryHandler] = {}
    
    def register_handler(self, query_type: Type, handler: QueryHandler) -> None:
        """Register a handler for a query type.
        
        Args:
            query_type: The query type
            handler: The handler instance
        """
        self.handlers[query_type] = handler
        logger.debug(f"Registered handler for {query_type}")
    
    async def send(self, query: Any) -> Any:
        """Send a query to be handled.
        
        Args:
            query: The query to handle
            
        Returns:
            Query result
        """
        query_type = type(query)
        handler = self.handlers.get(query_type)
        
        if not handler:
            raise ValueError(f"No handler registered for query type: {query_type}")
        
        logger.debug(f"Handling query: {query_type}")
        return await handler.handle(query)