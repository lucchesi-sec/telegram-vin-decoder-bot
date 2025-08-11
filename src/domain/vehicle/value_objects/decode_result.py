"""Decode Result value object."""

from typing import Dict, Any, Optional


class DecodeResult:
    """Value object representing a VIN decode result."""
    
    def __init__(
        self,
        success: bool,
        vin: str,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        model_year: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None,
        service_used: Optional[str] = None,
        error_message: Optional[str] = None,
        raw_response: Optional[Dict[str, Any]] = None
    ):
        """Initialize decode result."""
        self.success = success
        self.vin = vin
        self.manufacturer = manufacturer
        self.model = model
        self.model_year = model_year
        self.attributes = attributes or {}
        self.service_used = service_used
        self.error_message = error_message
        self.raw_response = raw_response
    
    def has_complete_data(self) -> bool:
        """Check if the decode result has complete data."""
        return all([
            self.success,
            self.manufacturer,
            self.model,
            self.model_year,
            self.attributes
        ])
    
    def get_display_string(self) -> str:
        """Get a display string for the decode result."""
        if not self.success:
            return f"Failed to decode VIN {self.vin}: {self.error_message}"
        
        parts = []
        if self.model_year:
            parts.append(str(self.model_year))
        if self.manufacturer:
            parts.append(self.manufacturer)
        if self.model:
            parts.append(self.model)
        
        display = " ".join(parts) if parts else "Unknown Vehicle"
        return f"{display} (VIN: {self.vin})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decode result to dictionary."""
        return {
            "success": self.success,
            "vin": self.vin,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "model_year": self.model_year,
            "attributes": self.attributes,
            "service_used": self.service_used,
            "error_message": self.error_message,
            "raw_response": self.raw_response
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecodeResult':
        """Create decode result from dictionary."""
        return cls(
            success=data.get("success", False),
            vin=data.get("vin", ""),
            manufacturer=data.get("manufacturer"),
            model=data.get("model"),
            model_year=data.get("model_year"),
            attributes=data.get("attributes", {}),
            service_used=data.get("service_used"),
            error_message=data.get("error_message"),
            raw_response=data.get("raw_response")
        )
    
    def __eq__(self, other: Any) -> bool:
        """Check equality with another decode result."""
        if not isinstance(other, DecodeResult):
            return False
        return (
            self.success == other.success and
            self.vin == other.vin and
            self.manufacturer == other.manufacturer and
            self.model == other.model and
            self.model_year == other.model_year and
            self.service_used == other.service_used
        )
    
    def __repr__(self) -> str:
        """Return detailed representation of the decode result."""
        return (
            f"DecodeResult(success={self.success}, vin='{self.vin}', "
            f"manufacturer='{self.manufacturer}', model='{self.model}', "
            f"model_year={self.model_year}, service_used='{self.service_used}')"
        )