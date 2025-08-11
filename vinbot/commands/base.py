"""Base class for command handlers."""

from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes


class CommandHandler(ABC):
    """Abstract base class for all command handlers."""
    
    @property
    @abstractmethod
    def command(self) -> str:
        """Return the command this handler responds to (without /)."""
        pass
    
    @property
    def description(self) -> str:
        """Return the command description for help text."""
        return ""
    
    @abstractmethod
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Execute the command.
        
        Args:
            update: The update that triggered the command
            context: The context for the command
        """
        pass