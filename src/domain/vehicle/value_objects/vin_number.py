"""VIN Number value object."""

import re
from typing import Any


class VINNumber:
    """Value object representing a vehicle identification number."""
    
    def __init__(self, value: str):
        """Initialize VIN number with validation."""
        # Normalize the VIN (uppercase, strip whitespace)
        normalized = value.strip().upper() if value else ""
        
        # Validate length
        if len(normalized) != 17:
            raise ValueError(f"VIN must be exactly 17 characters, got {len(normalized)}")
        
        # Validate characters (VINs don't contain I, O, or Q)
        if not self._validate_characters(normalized):
            raise ValueError(f"VIN contains invalid characters: {value}")
        
        self._value = normalized
    
    @property
    def value(self) -> str:
        """Get the VIN value."""
        return self._value
    
    @staticmethod
    def _validate_characters(vin: str) -> bool:
        """Check if the VIN contains only valid characters."""
        # VIN regex pattern (excluding I, O, Q characters)
        pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
        return bool(re.match(pattern, vin))
    
    def is_valid(self) -> bool:
        """Check if the VIN is valid."""
        return len(self._value) == 17 and self._validate_characters(self._value)
    
    def get_manufacturer_code(self) -> str:
        """Get the manufacturer code (first 3 characters)."""
        return self._value[:3]
    
    def get_year_code(self) -> str:
        """Get the year code (10th character)."""
        return self._value[9]
    
    def __str__(self) -> str:
        """Return string representation of the VIN."""
        return self._value
    
    def __repr__(self) -> str:
        """Return detailed representation of the VIN."""
        return f"VINNumber('{self._value}')"
    
    def __eq__(self, other: Any) -> bool:
        """Check equality with another VIN."""
        if isinstance(other, VINNumber):
            return self._value == other._value
        return False
    
    def __hash__(self) -> int:
        """Return hash of the VIN."""
        return hash(self._value)