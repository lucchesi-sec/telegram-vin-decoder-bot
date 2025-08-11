"""In-memory vehicle repository implementation."""

import asyncio
import logging
from typing import Optional, List, Dict
from src.domain.vehicle.entities.vehicle import Vehicle
from src.domain.vehicle.repositories.vehicle_repository import VehicleRepository
from src.domain.vehicle.value_objects import VINNumber


class InMemoryVehicleRepository(VehicleRepository):
    """In-memory implementation of VehicleRepository for testing."""
    
    def __init__(self):
        self._vehicles: Dict[str, Vehicle] = {}
        self._vin_index: Dict[str, str] = {}  # VIN -> vehicle_id
        self._lock = asyncio.Lock()
    
    async def save(self, vehicle: Vehicle) -> None:
        """Save a vehicle aggregate."""
        async with self._lock:
            self._vehicles[vehicle.id] = vehicle
            self._vin_index[vehicle.vin.value] = vehicle.id
    
    async def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """Find a vehicle by its ID."""
        async with self._lock:
            return self._vehicles.get(vehicle_id)
    
    async def find_by_vin(self, vin: VINNumber) -> Optional[Vehicle]:
        """Find a vehicle by its VIN."""
        async with self._lock:
            vehicle_id = self._vin_index.get(vin.value)
            if vehicle_id:
                return self._vehicles.get(vehicle_id)
            return None
    
    async def find_all(self) -> List[Vehicle]:
        """Find all vehicles."""
        async with self._lock:
            return list(self._vehicles.values())
    
    async def delete(self, vehicle_id: str) -> bool:
        """Delete a vehicle by its ID."""
        async with self._lock:
            if vehicle_id in self._vehicles:
                vehicle = self._vehicles[vehicle_id]
                del self._vin_index[vehicle.vin.value]
                del self._vehicles[vehicle_id]
                return True
            return False