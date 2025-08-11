"""VIN entity."""

from dataclasses import dataclass
from src.domain.shared.entity import Entity
from src.domain.vehicle.value_objects import VINNumber


@dataclass
class VIN(Entity):
    """VIN entity representing a vehicle identification number."""
    
    value: VINNumber
    
    def __post_init__(self):
        """Initialize the VIN entity."""
        super().__post_init__()
        # Additional initialization logic if needed