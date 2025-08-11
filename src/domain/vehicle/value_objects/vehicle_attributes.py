"""Vehicle attributes value object."""

from dataclasses import dataclass
from typing import Dict, Any
from src.domain.shared.entity import ValueObject


@dataclass(frozen=True)
class VehicleAttributes(ValueObject):
    """Value object representing vehicle attributes."""
    
    data: Dict[str, Any]
    
    def __post_init__(self):
        """Validate the vehicle attributes."""
        # Add validation logic if needed
        pass
    
    def get(self, key: str, default=None) -> Any:
        """Get an attribute value by key."""
        return self.data.get(key, default)
    
    def has(self, key: str) -> bool:
        """Check if an attribute exists."""
        return key in self.data