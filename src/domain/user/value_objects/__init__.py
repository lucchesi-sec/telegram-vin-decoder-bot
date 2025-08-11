"""User domain value objects."""

from dataclasses import dataclass
from src.domain.shared.entity import ValueObject


@dataclass(frozen=True)
class TelegramID(ValueObject):
    """Value object representing a Telegram user ID."""
    
    value: int
    
    def __post_init__(self):
        """Validate the Telegram ID."""
        if self.value <= 0:
            raise ValueError(f"Telegram ID must be positive, got {self.value}")
    
    def __str__(self) -> str:
        """Return string representation of the Telegram ID."""
        return str(self.value)


@dataclass(frozen=True)
class UserPreferences(ValueObject):
    """Value object representing user preferences."""
    
    preferred_service: str = "NHTSA"
    autodev_api_key: str = ""
    nhtsa_api_key: str = ""
    
    def __post_init__(self):
        """Validate user preferences."""
        # Add validation logic if needed
        pass


@dataclass(frozen=True)
class SubscriptionTier(ValueObject):
    """Value object representing a user's subscription tier."""
    
    tier_name: str
    features: list = None
    
    def __post_init__(self):
        """Initialize subscription tier."""
        if self.features is None:
            object.__setattr__(self, 'features', [])