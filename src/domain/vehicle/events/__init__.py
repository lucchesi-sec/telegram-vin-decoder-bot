"""Vehicle domain events."""

from dataclasses import dataclass, field
from datetime import datetime
from src.domain.shared.domain_event import DomainEvent


@dataclass
class VehicleDecodedEvent(DomainEvent):
    """Event raised when a vehicle is successfully decoded."""
    
    vin: str = ""
    decoded_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Initialize vehicle_id from aggregate_id."""
        if not self.aggregate_id and self.vin:
            self.aggregate_id = f"vehicle_{self.vin}"
        self.vehicle_id = self.aggregate_id


@dataclass
class DecodeFailedEvent(DomainEvent):
    """Event raised when a VIN decode attempt fails."""
    
    vin: str = ""
    service_used: str = ""
    error_message: str = ""
    failed_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Initialize aggregate_id if not set."""
        if not self.aggregate_id and self.vin:
            self.aggregate_id = f"vehicle_{self.vin}"