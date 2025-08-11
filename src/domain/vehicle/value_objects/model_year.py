"""Model Year value object."""

from datetime import datetime
from typing import Any


class ModelYear:
    """Value object representing a vehicle model year."""
    
    def __init__(self, value: int):
        """Initialize model year with validation."""
        current_year = datetime.now().year
        
        # Most systems track vehicles from 1980 onwards
        # Allow up to 2 years in the future for new models
        if value < 1980 or value > current_year + 2:
            raise ValueError(f"Model year must be between 1980 and {current_year + 2}, got {value}")
        
        self._value = value
    
    @property
    def value(self) -> int:
        """Get the model year value."""
        return self._value
    
    def is_valid(self) -> bool:
        """Check if the model year is valid."""
        current_year = datetime.now().year
        return 1980 <= self._value <= current_year + 2
    
    def get_age(self) -> int:
        """Get the age of the vehicle in years."""
        current_year = datetime.now().year
        return current_year - self._value
    
    def is_classic(self) -> bool:
        """Check if the vehicle is classic (25+ years old)."""
        return self.get_age() >= 25
    
    def __str__(self) -> str:
        """Return string representation of the model year."""
        return str(self._value)
    
    def __repr__(self) -> str:
        """Return detailed representation of the model year."""
        return f"ModelYear({self._value})"
    
    def __eq__(self, other: Any) -> bool:
        """Check equality with another model year."""
        if isinstance(other, ModelYear):
            return self._value == other._value
        return False
    
    def __lt__(self, other: 'ModelYear') -> bool:
        """Check if this year is less than another."""
        if isinstance(other, ModelYear):
            return self._value < other._value
        return NotImplemented
    
    def __le__(self, other: 'ModelYear') -> bool:
        """Check if this year is less than or equal to another."""
        if isinstance(other, ModelYear):
            return self._value <= other._value
        return NotImplemented
    
    def __gt__(self, other: 'ModelYear') -> bool:
        """Check if this year is greater than another."""
        if isinstance(other, ModelYear):
            return self._value > other._value
        return NotImplemented
    
    def __ge__(self, other: 'ModelYear') -> bool:
        """Check if this year is greater than or equal to another."""
        if isinstance(other, ModelYear):
            return self._value >= other._value
        return NotImplemented
    
    def __hash__(self) -> int:
        """Return hash of the model year."""
        return hash(self._value)