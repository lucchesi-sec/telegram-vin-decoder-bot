"""Vehicle DTOs for API responses following DDD principles."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from src.domain.vehicle.entities.vehicle import Vehicle


class VehicleDecodeRequestDTO(BaseModel):
    """Request DTO for VIN decoding."""
    vin: str = Field(..., min_length=17, max_length=17, description="17-character VIN")


class VehicleResponseDTO(BaseModel):
    """Response DTO for vehicle data."""
    id: Optional[int] = None
    vin: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vehicle_type: Optional[str] = None
    engine_info: Optional[str] = None
    fuel_type: Optional[str] = None
    decoded_at: Optional[datetime] = None
    user_id: Optional[int] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_domain(cls, vehicle: Vehicle) -> "VehicleResponseDTO":
        """Convert domain Vehicle entity to DTO."""
        return cls(
            id=vehicle.id.value if vehicle.id else None,
            vin=vehicle.vin.value,
            manufacturer=vehicle.info.manufacturer if vehicle.info else None,
            model=vehicle.info.model if vehicle.info else None,
            year=vehicle.info.year.value if vehicle.info and vehicle.info.year else None,
            vehicle_type=vehicle.info.vehicle_type if vehicle.info else None,
            engine_info=vehicle.info.engine_info if vehicle.info else None,
            fuel_type=vehicle.info.fuel_type if vehicle.info else None,
            decoded_at=vehicle.decoded_at,
            user_id=vehicle.user_id.value if vehicle.user_id else None,
            raw_data=vehicle.raw_data or {}
        )


class VehicleDecodeResponseDTO(BaseModel):
    """Response DTO for VIN decode operation."""
    success: bool
    vehicle: Optional[VehicleResponseDTO] = None
    error: Optional[str] = None