"""Vehicle application service."""

import logging
from typing import Optional
from src.domain.vehicle.value_objects import VINNumber, DecodeResult
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.application.shared.command_bus import CommandBus
from src.application.shared.query_bus import QueryBus
from src.application.vehicle.commands import DecodeVINCommand, GetVehicleHistoryQuery

logger = logging.getLogger(__name__)


class VehicleApplicationService:
    """Application service for vehicle-related operations."""
    
    def __init__(
        self,
        command_bus: CommandBus,
        query_bus: QueryBus,
        logger: logging.Logger
    ):
        self.command_bus = command_bus
        self.query_bus = query_bus
        self.logger = logger
    
    async def decode_vin(
        self,
        vin: str,
        user_preferences: UserPreferences,
        force_refresh: bool = False
    ) -> DecodeResult:
        """Decode a VIN using the appropriate service.
        
        Args:
            vin: The VIN to decode
            user_preferences: User's service preferences
            force_refresh: Whether to force a fresh decode
            
        Returns:
            Decode result
        """
        try:
            # Create VIN number value object
            vin_number = VINNumber(vin)
            
            # Create command
            command = DecodeVINCommand(
                vin=vin_number,
                user_preferences=user_preferences,
                force_refresh=force_refresh
            )
            
            # Send command via command bus
            result = await self.command_bus.send(command)
            return result
        except Exception as e:
            self.logger.error(f"Error in decode_vin: {e}")
            raise
    
    async def get_vehicle_history(self, vehicle_id: str) -> list:
        """Get decode history for a vehicle.
        
        Args:
            vehicle_id: The vehicle ID
            
        Returns:
            List of decode attempts
        """
        try:
            # Create query
            query = GetVehicleHistoryQuery(vehicle_id=vehicle_id)
            
            # Send query via query bus
            result = await self.query_bus.send(query)
            return result
        except Exception as e:
            self.logger.error(f"Error in get_vehicle_history: {e}")
            raise