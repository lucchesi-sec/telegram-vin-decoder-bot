"""Simple command bus implementation."""

import logging
from typing import Dict, Type, Any
from src.application.shared.command_bus import CommandBus, CommandHandler

logger = logging.getLogger(__name__)


class SimpleCommandBus(CommandBus):
    """Simple implementation of command bus."""
    
    def __init__(self):
        self.handlers: Dict[Type, CommandHandler] = {}
    
    def register_handler(self, command_type: Type, handler: CommandHandler) -> None:
        """Register a handler for a command type.
        
        Args:
            command_type: The command type
            handler: The handler instance
        """
        self.handlers[command_type] = handler
        logger.debug(f"Registered handler for {command_type}")
    
    async def send(self, command: Any) -> Any:
        """Send a command to be handled.
        
        Args:
            command: The command to handle
            
        Returns:
            Command result
        """
        command_type = type(command)
        handler = self.handlers.get(command_type)
        
        if not handler:
            raise ValueError(f"No handler registered for command type: {command_type}")
        
        logger.debug(f"Handling command: {command_type}")
        return await handler.handle(command)