"""Command bus for handling commands."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

Command = TypeVar('Command')
CommandResult = TypeVar('CommandResult')


class CommandHandler(ABC, Generic[Command, CommandResult]):
    """Base class for command handlers."""
    
    @abstractmethod
    async def handle(self, command: Command) -> CommandResult:
        """Handle a command."""
        pass


class CommandBus(ABC):
    """Interface for command bus."""
    
    @abstractmethod
    async def send(self, command: Any) -> Any:
        """Send a command to be handled."""
        pass