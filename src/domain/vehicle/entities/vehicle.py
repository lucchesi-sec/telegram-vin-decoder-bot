"""Vehicle domain entities."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.domain.shared.entity import AggregateRoot
from src.domain.vehicle.value_objects import VINNumber, ModelYear
from src.domain.vehicle.events import VehicleDecodedEvent


@dataclass
class BasicInfo:
    """Basic vehicle information."""
    vin: str = ""
    manufacturer: str = ""
    model: str = ""
    model_year: int = 0
    body_class: str = ""
    vehicle_type: str = ""
    gross_vehicle_weight_rating: str = ""
    manufacturer_address: str = ""
    plant_city: str = ""
    plant_country: str = ""
    plant_state: str = ""


@dataclass
class Specifications:
    """Vehicle specifications."""
    displacement_cc: Optional[float] = None
    displacement_ci: Optional[float] = None
    displacement_l: Optional[float] = None
    engine_cylinders: Optional[int] = None
    engine_model: str = ""
    fuel_type_primary: str = ""
    electrification_level: str = ""
    other_engine_info: str = ""
    turbo: Optional[bool] = None
    drive_type: str = ""
    transmission_style: str = ""
    transmission_speeds: str = ""
    doors: Optional[int] = None
    seats: Optional[int] = None
    wheel_base_type: str = ""
    bed_type: str = ""
    cab_type: str = ""


@dataclass
class DecodeAttempt:
    """Represents a single decode attempt for a vehicle."""
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    service_used: str = ""
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class Vehicle(AggregateRoot):
    """Vehicle aggregate root."""
    
    vin: VINNumber = None
    manufacturer: str = ""
    model: str = ""
    model_year: ModelYear = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    decode_history: List[DecodeAttempt] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the vehicle and emit decoded event if newly created."""
        # Initialize domain events list if not already done
        if not hasattr(self, '_domain_events'):
            self._domain_events = []
        # In a real implementation, we would check if this is a newly decoded vehicle
        # and emit an event accordingly. For now, we'll skip this to avoid circular imports.
        # In practice, this would be handled in a factory method.
    
    def update_attributes(self, new_attributes: Dict[str, Any]) -> None:
        """Update vehicle attributes with business logic validation."""
        # Add business logic validation here
        self.attributes.update(new_attributes)
        self.updated_at = datetime.utcnow()
    
    def add_decode_attempt(self, attempt: DecodeAttempt) -> None:
        """Add a decode attempt to the vehicle's history."""
        self.decode_history.append(attempt)
    
    @classmethod
    def create_from_decode_result(
        cls, 
        vin: VINNumber, 
        manufacturer: str, 
        model: str, 
        model_year: ModelYear,
        attributes: Dict[str, Any],
        service_used: str
    ) -> 'Vehicle':
        """Factory method for creating a Vehicle from decode result."""
        vehicle = cls(
            vin=vin,
            manufacturer=manufacturer,
            model=model,
            model_year=model_year,
            attributes=attributes
        )
        
        # Add successful decode attempt
        attempt = DecodeAttempt(
            timestamp=datetime.utcnow(),
            service_used=service_used,
            success=True
        )
        vehicle.add_decode_attempt(attempt)
        
        # Emit domain event
        vehicle.add_domain_event(VehicleDecodedEvent(
            aggregate_id=vehicle.id,
            vin=vin.value,
            decoded_at=datetime.utcnow()
        ))
        
        return vehicle
    
    @property
    def display_representation(self) -> str:
        """Get display representation of the vehicle."""
        parts = []
        if self.manufacturer:
            parts.append(self.manufacturer)
        if self.model:
            parts.append(self.model)
        return " ".join(parts)