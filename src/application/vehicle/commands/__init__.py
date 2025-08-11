"""Vehicle application commands."""

from dataclasses import dataclass
from src.domain.vehicle.value_objects import VINNumber
from src.domain.user.value_objects.user_preferences import UserPreferences


@dataclass
class DecodeVINCommand:
    """Command to decode a VIN."""
    
    vin: VINNumber
    user_preferences: UserPreferences
    force_refresh: bool = False


@dataclass
class GetVehicleHistoryQuery:
    """Query to get vehicle decode history."""
    
    vehicle_id: str