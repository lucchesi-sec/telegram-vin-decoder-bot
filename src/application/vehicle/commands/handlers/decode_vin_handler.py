"""Vehicle command handlers."""

import logging
from typing import Any
from datetime import datetime, timezone
from src.application.shared.command_bus import CommandHandler
from src.application.vehicle.commands import DecodeVINCommand
from src.domain.vehicle.repositories import VehicleRepository
from src.domain.vehicle.value_objects import DecodeResult, VINNumber
from src.domain.vehicle.entities.vehicle import Vehicle, DecodeAttempt
from src.domain.vehicle.events import DecodeFailedEvent
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
            
            # Try auto.dev decoder first, fallback to NHTSA if it fails
            primary_decoder = self.decoder_factory.autodev_adapter
            fallback_decoder = self.decoder_factory.nhtsa_adapter
            
            # Perform decoding with fallback pattern
            raw_result = None
            
            # Try primary decoder (auto.dev)
            if primary_decoder.client.api_key:
                try:
                    self.logger.info(f"Attempting to decode VIN {command.vin} with auto.dev")
                    raw_result = await primary_decoder.decode(command.vin)
                    self.logger.info(f"Successfully decoded VIN {command.vin} with auto.dev")
                except Exception as e:
                    self.logger.warning(f"auto.dev decode failed for VIN {command.vin}: {e}, falling back to NHTSA")
            
            # Fallback to NHTSA if auto.dev failed or is not configured
            if raw_result is None:
                try:
                    self.logger.info(f"Attempting to decode VIN {command.vin} with NHTSA")
                    raw_result = await fallback_decoder.decode(command.vin)
                    self.logger.info(f"Successfully decoded VIN {command.vin} with NHTSA")
                except Exception as e:
                    # Both decoders failed
                    self.logger.error(f"All decoders failed for VIN {command.vin}: {e}")
                    await self.event_bus.publish(DecodeFailedEvent(
                        vin=command.vin.value,
                        service_used="auto.dev/NHTSA",
                        error_message=str(e),
                        failed_at=datetime.now(timezone.utc)
                    ))
                    raise ApplicationException("Unable to decode VIN", cause=e)
            
            # Create vehicle from decode result
            vehicle = self._create_vehicle_from_result(command.vin, raw_result)
            await self.vehicle_repo.save(vehicle)
            
            # Publish domain events
            for event in vehicle.collect_events():
                await self.event_bus.publish(event)
            
            return self._vehicle_to_decode_result(vehicle)
        except Exception as e:
            self.logger.error(f"Error handling decode VIN command: {e}")
            raise
    
    def _create_vehicle_from_result(self, vin: VINNumber, raw_result: dict) -> Vehicle:
        """Create a vehicle entity from raw decode result."""
        from src.domain.vehicle.value_objects import ModelYear
        from src.domain.vehicle.entities.vehicle import BasicInfo, Specifications
        
        # Handle different response formats from various services
        attributes = raw_result.get("attributes", {})
        
        # Extract manufacturer - could be in attributes or top-level
        manufacturer = (
            attributes.get("manufacturer") or 
            attributes.get("make") or 
            raw_result.get("manufacturer", "Unknown")
        )
        
        # Extract model - could be in attributes or top-level
        model = (
            attributes.get("model") or 
            raw_result.get("model", "Unknown")
        )
        
        # Extract year - could be in attributes or top-level
        year_value = (
            attributes.get("year") or 
            attributes.get("model_year") or 
            raw_result.get("year") or 
            raw_result.get("model_year") or 
            "2020"
        )
        
        # Ensure year is a valid integer
        try:
            year = int(str(year_value))
        except (ValueError, TypeError):
            year = 2020
            
        # Create BasicInfo object
        basic_info = BasicInfo(
            vin=vin.value,
            manufacturer=manufacturer,
            model=model,
            model_year=year,
            body_class=attributes.get("body_class", ""),
            vehicle_type=attributes.get("vehicle_type", ""),
            gross_vehicle_weight_rating=attributes.get("gross_vehicle_weight_rating", ""),
            manufacturer_address=attributes.get("manufacturer_address", ""),
            plant_city=attributes.get("plant_city", ""),
            plant_country=attributes.get("plant_country", ""),
            plant_state=attributes.get("plant_state", "")
        )
        
        # Create Specifications object
        specifications = Specifications(
            displacement_cc=attributes.get("displacement_cc"),
            displacement_ci=attributes.get("displacement_ci"),
            displacement_l=attributes.get("displacement_l"),
            engine_cylinders=attributes.get("engine_cylinders"),
            engine_model=attributes.get("engine_model", ""),
            fuel_type_primary=attributes.get("fuel_type_primary", ""),
            electrification_level=attributes.get("electrification_level", ""),
            other_engine_info=attributes.get("other_engine_info", ""),
            turbo=attributes.get("turbo"),
            drive_type=attributes.get("drive_type", ""),
            transmission_style=attributes.get("transmission_style", ""),
            transmission_speeds=attributes.get("transmission_speeds", ""),
            doors=attributes.get("doors"),
            seats=attributes.get("seats"),
            wheel_base_type=attributes.get("wheel_base_type", ""),
            bed_type=attributes.get("bed_type", ""),
            cab_type=attributes.get("cab_type", "")
        )
        
        vehicle = Vehicle(
            vin=vin,
            manufacturer=manufacturer,
            model=model,
            model_year=ModelYear(year),
            attributes=attributes if attributes else raw_result,
            basic_info=basic_info,
            specifications=specifications,
            service_used=raw_result.get("service", "Unknown"),
            raw_data=raw_result
        )
        
        # Add successful decode attempt
        attempt = DecodeAttempt(
            timestamp=datetime.now(timezone.utc),
            service_used=raw_result.get("service", "Unknown"),
            success=True
        )
        vehicle.add_decode_attempt(attempt)
        
        return vehicle
    
    def _vehicle_to_decode_result(self, vehicle: Vehicle) -> DecodeResult:
        """Convert a vehicle entity to a decode result."""
        # Get service used from the most recent decode attempt
        service_used = "Unknown"
        if vehicle.decode_history:
            service_used = vehicle.decode_history[-1].service_used
            
        return DecodeResult(
            vin=str(vehicle.vin),
            success=True,
            manufacturer=vehicle.manufacturer,
            model=vehicle.model,
            model_year=vehicle.model_year.value if vehicle.model_year else None,
            attributes=vehicle.attributes,
            service_used=service_used
        )


class ApplicationException(Exception):
    """Application layer exception."""
    
    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message)
        self.cause = cause