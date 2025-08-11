"""Command registry for managing and dispatching commands."""

import logging
from typing import Dict, List
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler as TelegramCommandHandler

from .base import CommandHandler

logger = logging.getLogger(__name__)


class CommandRegistry:
    """Registry for managing command handlers."""
    
    def __init__(self):
        """Initialize the command registry."""
        self._handlers: Dict[str, CommandHandler] = {}
    
    def register(self, handler: CommandHandler) -> None:
        """Register a command handler.
        
        Args:
            handler: The command handler to register
        """
        command = handler.command
        if command in self._handlers:
            logger.warning(f"Command {command} is already registered, overwriting")
        
        self._handlers[command] = handler
        logger.info(f"Registered command: {command}")
    
    def get_handler(self, command: str) -> CommandHandler | None:
        """Get a handler for a specific command.
        
        Args:
            command: The command to get the handler for
            
        Returns:
            The command handler or None if not found
        """
        return self._handlers.get(command)
    
    def get_telegram_handlers(self) -> List[TelegramCommandHandler]:
        """Get Telegram command handlers for all registered commands.
        
        Returns:
            List of Telegram CommandHandler instances
        """
        handlers = []
        for command, handler in self._handlers.items():
            # Create a closure to capture the handler
            def make_wrapper(h):
                async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
                    await h.execute(update, context)
                return wrapper
            
            handlers.append(TelegramCommandHandler(command, make_wrapper(handler)))
        
        return handlers
    
    def get_help_text(self) -> str:
        """Generate help text from all registered commands.
        
        Returns:
            Formatted help text string
        """
        help_lines = [
            "📚 **Available Commands:**",
            ""
        ]
        
        for command, handler in sorted(self._handlers.items()):
            if handler.description:
                help_lines.append(f"/{command} - {handler.description}")
            else:
                help_lines.append(f"/{command}")
        
        return "\n".join(help_lines)