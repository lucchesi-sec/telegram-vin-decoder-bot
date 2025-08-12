"""PostgreSQL vehicle repository implementation."""

import logging
import uuid
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.vehicle.entities.vehicle import Vehicle, BasicInfo, Specifications
from src.domain.vehicle.repositories.vehicle_repository import VehicleRepository
from src.domain.vehicle.value_objects import VINNumber
from src.infrastructure.persistence.models import VehicleModel


logger = logging.getLogger(__name__)


class PostgreSQLVehicleRepository(VehicleRepository):
    """PostgreSQL implementation of vehicle repository."""
    
    def __init__(self, session_factory):
        """Initialize the repository.
        
        Args:
            session_factory: SQLAlchemy async session factory
        """
        self.session_factory = session_factory
    
    async def save(self, vehicle: Vehicle) -> None:
        """Save a vehicle aggregate.
        
        Args:
            vehicle: Vehicle to save
        """
        async with self.session_factory() as session:
            # Check if vehicle exists
            result = await session.execute(
                select(VehicleModel).where(VehicleModel.id == vehicle.id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing vehicle
                await session.execute(
                    update(VehicleModel)
                    .where(VehicleModel.id == vehicle.id)
                    .values(
                        vin=vehicle.vin.value,
                        make=vehicle.basic_info.manufacturer if vehicle.basic_info else None,
                        model=vehicle.basic_info.model if vehicle.basic_info else None,
                        year=vehicle.basic_info.model_year if vehicle.basic_info else None,
                        manufacturer=vehicle.basic_info.manufacturer if vehicle.basic_info else None,
                        service_used=vehicle.service_used,
                        raw_data=vehicle.raw_data,
                        basic_info=self._basic_info_to_dict(vehicle.basic_info),
                        specifications=self._specifications_to_dict(vehicle.specifications),
                        safety_ratings=vehicle.safety_ratings,
                        error_message=vehicle.error_message,
                        expires_at=datetime.utcnow() + timedelta(days=90)
                    )
                )
            else:
                # Create new vehicle
                vehicle_model = VehicleModel(
                    id=vehicle.id,
                    vin=vehicle.vin.value,
                    make=vehicle.basic_info.manufacturer if vehicle.basic_info else None,
                    model=vehicle.basic_info.model if vehicle.basic_info else None,
                    year=vehicle.basic_info.model_year if vehicle.basic_info else None,
                    manufacturer=vehicle.basic_info.manufacturer if vehicle.basic_info else None,
                    service_used=vehicle.service_used,
                    raw_data=vehicle.raw_data,
                    basic_info=self._basic_info_to_dict(vehicle.basic_info),
                    specifications=self._specifications_to_dict(vehicle.specifications),
                    safety_ratings=vehicle.safety_ratings,
                    error_message=vehicle.error_message,
                    decoded_at=vehicle.decoded_at,
                    expires_at=datetime.utcnow() + timedelta(days=90)
                )
                session.add(vehicle_model)
            
            await session.commit()
            logger.info(f"Saved vehicle: {vehicle.id} with VIN: {vehicle.vin.value}")
    
    async def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """Find a vehicle by its ID.
        
        Args:
            vehicle_id: Vehicle ID
            
        Returns:
            Vehicle if found, None otherwise
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(VehicleModel).where(VehicleModel.id == vehicle_id)
            )
            vehicle_model = result.scalar_one_or_none()
            
            if vehicle_model:
                return self._to_domain(vehicle_model)
            return None
    
    async def find_by_vin(self, vin: VINNumber) -> Optional[Vehicle]:
        """Find a vehicle by its VIN.
        
        Args:
            vin: Vehicle VIN
            
        Returns:
            Vehicle if found, None otherwise
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(VehicleModel)
                .where(VehicleModel.vin == vin.value)
                .where(VehicleModel.expires_at > datetime.utcnow())
            )
            vehicle_model = result.scalar_one_or_none()
            
            if vehicle_model:
                logger.info(f"Found cached vehicle for VIN: {vin.value}")
                return self._to_domain(vehicle_model)
            
            logger.info(f"No cached vehicle found for VIN: {vin.value}")
            return None
    
    async def find_all(self) -> List[Vehicle]:
        """Find all vehicles.
        
        Returns:
            List of all vehicles
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(VehicleModel)
                .order_by(VehicleModel.decoded_at.desc())
                .limit(1000)  # Limit for safety
            )
            vehicle_models = result.scalars().all()
            
            return [self._to_domain(model) for model in vehicle_models]
    
    async def delete(self, vehicle_id: str) -> bool:
        """Delete a vehicle by its ID.
        
        Args:
            vehicle_id: Vehicle ID
            
        Returns:
            True if deleted, False if not found
        """
        async with self.session_factory() as session:
            result = await session.execute(
                delete(VehicleModel).where(VehicleModel.id == vehicle_id)
            )
            await session.commit()
            
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Deleted vehicle: {vehicle_id}")
            
            return deleted
    
    async def cleanup_expired(self) -> int:
        """Clean up expired vehicle cache entries.
        
        Returns:
            Number of deleted entries
        """
        async with self.session_factory() as session:
            result = await session.execute(
                delete(VehicleModel)
                .where(VehicleModel.expires_at < datetime.utcnow())
            )
            await session.commit()
            
            count = result.rowcount
            if count > 0:
                logger.info(f"Cleaned up {count} expired vehicle cache entries")
            
            return count
    
    def _to_domain(self, model: VehicleModel) -> Vehicle:
        """Convert database model to domain entity.
        
        Args:
            model: Database model
            
        Returns:
            Domain entity
        """
        basic_info = None
        if model.basic_info:
            basic_info = BasicInfo(
                vin=model.basic_info.get('vin', ''),
                manufacturer=model.basic_info.get('manufacturer', ''),
                model=model.basic_info.get('model', ''),
                model_year=model.basic_info.get('model_year', 0),
                body_class=model.basic_info.get('body_class', ''),
                vehicle_type=model.basic_info.get('vehicle_type', ''),
                gross_vehicle_weight_rating=model.basic_info.get('gross_vehicle_weight_rating', ''),
                manufacturer_address=model.basic_info.get('manufacturer_address', ''),
                plant_city=model.basic_info.get('plant_city', ''),
                plant_country=model.basic_info.get('plant_country', ''),
                plant_state=model.basic_info.get('plant_state', '')
            )
        
        specifications = None
        if model.specifications:
            specifications = Specifications(
                displacement_cc=model.specifications.get('displacement_cc'),
                displacement_ci=model.specifications.get('displacement_ci'),
                displacement_l=model.specifications.get('displacement_l'),
                engine_cylinders=model.specifications.get('engine_cylinders'),
                engine_model=model.specifications.get('engine_model', ''),
                fuel_type_primary=model.specifications.get('fuel_type_primary', ''),
                electrification_level=model.specifications.get('electrification_level', ''),
                other_engine_info=model.specifications.get('other_engine_info', ''),
                turbo=model.specifications.get('turbo'),
                drive_type=model.specifications.get('drive_type', ''),
                transmission_style=model.specifications.get('transmission_style', ''),
                transmission_speeds=model.specifications.get('transmission_speeds', ''),
                doors=model.specifications.get('doors'),
                seats=model.specifications.get('seats'),
                wheel_base_type=model.specifications.get('wheel_base_type', ''),
                bed_type=model.specifications.get('bed_type', ''),
                cab_type=model.specifications.get('cab_type', '')
            )
        
        from src.domain.vehicle.value_objects import ModelYear
        
        return Vehicle(
            id=model.id,
            vin=VINNumber(model.vin),
            manufacturer=model.manufacturer or "",
            model=model.model or "",
            model_year=ModelYear(model.year) if model.year else None,
            basic_info=basic_info,
            specifications=specifications,
            safety_ratings=model.safety_ratings,
            raw_data=model.raw_data,
            service_used=model.service_used,
            decoded_at=model.decoded_at,
            error_message=model.error_message
        )
    
    def _basic_info_to_dict(self, basic_info: Optional[BasicInfo]) -> Optional[dict]:
        """Convert BasicInfo to dictionary.
        
        Args:
            basic_info: BasicInfo object
            
        Returns:
            Dictionary representation
        """
        if not basic_info:
            return None
        
        return {
            'vin': basic_info.vin,
            'manufacturer': basic_info.manufacturer,
            'model': basic_info.model,
            'model_year': basic_info.model_year,
            'body_class': basic_info.body_class,
            'vehicle_type': basic_info.vehicle_type,
            'gross_vehicle_weight_rating': basic_info.gross_vehicle_weight_rating,
            'manufacturer_address': basic_info.manufacturer_address,
            'plant_city': basic_info.plant_city,
            'plant_country': basic_info.plant_country,
            'plant_state': basic_info.plant_state
        }
    
    def _specifications_to_dict(self, specs: Optional[Specifications]) -> Optional[dict]:
        """Convert Specifications to dictionary.
        
        Args:
            specs: Specifications object
            
        Returns:
            Dictionary representation
        """
        if not specs:
            return None
        
        return {
            'displacement_cc': specs.displacement_cc,
            'displacement_ci': specs.displacement_ci,
            'displacement_l': specs.displacement_l,
            'engine_cylinders': specs.engine_cylinders,
            'engine_model': specs.engine_model,
            'fuel_type_primary': specs.fuel_type_primary,
            'electrification_level': specs.electrification_level,
            'other_engine_info': specs.other_engine_info,
            'turbo': specs.turbo,
            'drive_type': specs.drive_type,
            'transmission_style': specs.transmission_style,
            'transmission_speeds': specs.transmission_speeds,
            'doors': specs.doors,
            'seats': specs.seats,
            'wheel_base_type': specs.wheel_base_type,
            'bed_type': specs.bed_type,
            'cab_type': specs.cab_type
        }