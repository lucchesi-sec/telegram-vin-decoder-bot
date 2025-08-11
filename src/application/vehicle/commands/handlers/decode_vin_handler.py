"""Vehicle command handlers."""

import logging
from typing import Optional, Any
from datetime import datetime
from src.application.shared.command_bus import CommandHandler
from src.application.vehicle.commands import DecodeVINCommand
from src.domain.vehicle.repositories import VehicleRepository
from src.domain.vehicle.value_objects import DecodeResult, VINNumber
from src.domain.vehicle.entities.vehicle import Vehicle
from src.domain.vehicle.events import VehicleDecodedEvent, DecodeFailedEvent
from src.application.shared.event_bus import EventBus

logger = logging.getLogger(__name__)


class DecodeVINHandler(CommandHandler[DecodeVINCommand, DecodeResult]):
    """Handler for decoding VIN commands."""
    
    def __init__(
        self,
        vehicle_repo: VehicleRepository,
        decoder_factory: Any,  # We'll define this interface later
        event_bus: EventBus,
        logger: logging.Logger
    ):
        self.vehicle_repo = vehicle_repo
        self.decoder_factory = decoder_factory
        self.event_bus = event_bus
        self.logger = logger
    
    async def handle(self, command: DecodeVINCommand) -> DecodeResult:
        """Handle a VIN decode command."""
        try:
            # Check cache first
            existing = await self.vehicle_repo.find_by_vin(command.vin)
            if existing and not command.force_refresh:
                # Convert vehicle to decode result
                return self._vehicle_to_decode_result(existing)
            
            # Select appropriate decoder based on user preferences
            decoder = self.decoder_factory.get_decoder(command.user_preferences)
            
            # Perform decoding with circuit breaker pattern
            try:
                raw_result = await decoder.decode(command.vin)
                # Create vehicle from decode result
                vehicle = self._create_vehicle_from_result(command.vin, raw_result)
                await self.vehicle_repo.save(vehicle)
                
                # Publish domain events
                for event in vehicle.collect_events():
                    await self.event_bus.publish(event)
                
                return self._vehicle_to_decode_result(vehicle)
            except Exception as e:
                # Handle decoder exception
                self.logger.error(f"Decoding failed for VIN {command.vin}: {e}")
                # Publish decode failed event
                await self.event_bus.publish(DecodeFailedEvent(
                    vin=command.vin.value,
                    service_used=decoder.service_name,
                    error_message=str(e),
                    failed_at=datetime.utcnow()
                ))
                raise ApplicationException("Unable to decode VIN", cause=e)
        except Exception as e:
            self.logger.error(f"Error handling decode VIN command: {e}")
            raise
    
    def _create_vehicle_from_result(self, vin: VINNumber, raw_result: dict) -> Vehicle:
        """Create a vehicle entity from raw decode result."""
        from src.domain.vehicle.value_objects import ModelYear
        
        return Vehicle.create_from_decode_result(
            vin=vin,
            manufacturer=raw_result.get("manufacturer", "Unknown"),
            model=raw_result.get("model", "Unknown"),
            model_year=ModelYear(int(raw_result.get("year", 2020))),
            attributes=raw_result,
            service_used=raw_result.get("service", "Unknown")
        )
    
    def _vehicle_to_decode_result(self, vehicle: Vehicle) -> DecodeResult:
        """Convert a vehicle entity to a decode result."""
        return DecodeResult(
            vin=str(vehicle.vin),
            success=True,
            manufacturer=vehicle.attributes.get("manufacturer"),
            model=vehicle.attributes.get("model"),
            model_year=vehicle.attributes.get("model_year"),
            attributes=vehicle.attributes,
            service_used="Unknown"  # This would come from the decode attempt
        )


class ApplicationException(Exception):
    """Application layer exception."""
    
    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message)
        self.cause = cause