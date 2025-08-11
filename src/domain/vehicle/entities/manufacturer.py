"""Manufacturer entity."""

from dataclasses import dataclass
from src.domain.shared.entity import Entity


@dataclass
class Manufacturer(Entity):
    """Manufacturer entity representing a vehicle manufacturer."""
    
    name: str
    country: str = ""
    
    def __post_init__(self):
        """Initialize the manufacturer entity."""
        super().__post_init__()
        # Additional initialization logic if needed