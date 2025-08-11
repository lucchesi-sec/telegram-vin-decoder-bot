"""TelegramID value object."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TelegramID:
    """Value object for Telegram user ID."""
    
    value: int
    
    def __post_init__(self):
        """Validate Telegram ID."""
        if not isinstance(self.value, int):
            raise ValueError("Telegram ID must be an integer")
        if self.value <= 0:
            raise ValueError("Telegram ID must be positive")
    
    def __str__(self) -> str:
        """String representation."""
        return str(self.value)
    
    def __eq__(self, other: Any) -> bool:
        """Equality comparison."""
        if not isinstance(other, TelegramID):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash(self.value)