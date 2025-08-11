"""Vehicle repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.vehicle.entities.vehicle import Vehicle
from src.domain.vehicle.value_objects import VINNumber


class VehicleRepository(ABC):
    """Repository interface for Vehicle aggregate."""
    
    @abstractmethod
    async def save(self, vehicle: Vehicle) -> None:
        """Save a vehicle aggregate."""
        pass
    
    @abstractmethod
    async def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """Find a vehicle by its ID."""
        pass
    
    @abstractmethod
    async def find_by_vin(self, vin: VINNumber) -> Optional[Vehicle]:
        """Find a vehicle by its VIN."""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[Vehicle]:
        """Find all vehicles."""
        pass
    
    @abstractmethod
    async def delete(self, vehicle_id: str) -> bool:
        """Delete a vehicle by its ID."""
        pass