"""Base callback strategy interface."""

from abc import ABC, abstractmethod
from typing import Optional
from telegram import CallbackQuery
from telegram.ext import ContextTypes


class CallbackStrategy(ABC):
    """Abstract base class for callback handlers."""
    
    @abstractmethod
    async def can_handle(self, callback_data: str) -> bool:
        """Check if this strategy can handle the given callback data.
        
        Args:
            callback_data: The callback data string from Telegram
            
        Returns:
            True if this strategy can handle the callback
        """
        pass
    
    @abstractmethod
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Handle the callback query.
        
        Args:
            query: The callback query from Telegram
            context: The bot context
            data: The callback data string
        """
        pass
    
    def extract_data(self, callback_data: str, prefix: str) -> Optional[str]:
        """Extract data from callback string after removing prefix.
        
        Args:
            callback_data: Full callback data string
            prefix: Prefix to remove
            
        Returns:
            Data after prefix, or None if prefix doesn't match
        """
        if callback_data.startswith(prefix):
            return callback_data[len(prefix):]
        return None