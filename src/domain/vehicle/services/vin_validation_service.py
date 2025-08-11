"""Vehicle domain services."""

import re
from typing import Tuple
from src.domain.vehicle.value_objects import VINNumber


class VINValidationService:
    """Domain service for VIN validation."""
    
    @staticmethod
    def validate_vin_format(vin: str) -> Tuple[bool, str]:
        """Validate VIN format.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not vin:
            return False, "VIN cannot be empty"
        
        if len(vin) != 17:
            return False, f"VIN must be 17 characters long, got {len(vin)}"
        
        # Check for invalid characters
        if not re.match(r'^[A-HJ-NPR-Z0-9]+$', vin.upper()):
            return False, "VIN contains invalid characters"
        
        # Check for excluded characters
        if any(char in vin.upper() for char in ['I', 'O', 'Q']):
            return False, "VIN cannot contain I, O, or Q characters"
        
        return True, ""
    
    @staticmethod
    def normalize_vin(vin: str) -> str:
        """Normalize VIN to uppercase."""
        return vin.strip().upper()