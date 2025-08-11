"""UserPreferences value object."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class UserPreferences:
    """Value object for user preferences."""

    preferred_decoder: str = (
        "autodev"  # Default to autodev, fallback handled in decoder
    )
    include_market_value: bool = True
    include_history: bool = True
    include_recalls: bool = True
    include_specs: bool = True
    format_preference: str = "standard"
    language: str = "en"
    notification_enabled: bool = False
    save_history: bool = True

    def __post_init__(self):
        """Validate preferences."""
        # Validate decoder - always use autodev with NHTSA fallback
        valid_decoders = ["nhtsa", "autodev", "carsxe"]
        if self.preferred_decoder not in valid_decoders:
            object.__setattr__(self, "preferred_decoder", "autodev")

        # Validate format preference
        valid_formats = ["standard", "detailed", "compact"]
        if self.format_preference not in valid_formats:
            object.__setattr__(self, "format_preference", "standard")

        # Validate language code
        valid_languages = ["en", "es", "fr", "de", "ru", "zh"]
        if self.language not in valid_languages:
            object.__setattr__(self, "language", "en")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "preferred_decoder": self.preferred_decoder,
            "include_market_value": self.include_market_value,
            "include_history": self.include_history,
            "include_recalls": self.include_recalls,
            "include_specs": self.include_specs,
            "format_preference": self.format_preference,
            "language": self.language,
            "notification_enabled": self.notification_enabled,
            "save_history": self.save_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferences":
        """Create from dictionary representation."""
        return cls(
            preferred_decoder=data.get("preferred_decoder", "autodev"),
            include_market_value=data.get("include_market_value", True),
            include_history=data.get("include_history", True),
            include_recalls=data.get("include_recalls", True),
            include_specs=data.get("include_specs", True),
            format_preference=data.get("format_preference", "standard"),
            language=data.get("language", "en"),
            notification_enabled=data.get("notification_enabled", False),
            save_history=data.get("save_history", True),
        )

    def with_decoder(self, decoder: str) -> "UserPreferences":
        """Create new preferences with updated decoder."""
        return UserPreferences(
            preferred_decoder=decoder,
            include_market_value=self.include_market_value,
            include_history=self.include_history,
            include_recalls=self.include_recalls,
            include_specs=self.include_specs,
            format_preference=self.format_preference,
            language=self.language,
            notification_enabled=self.notification_enabled,
            save_history=self.save_history,
        )
