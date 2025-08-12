"""Domain-driven API server using proper DDD architecture."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dependency_injector.wiring import Provide, inject

from src.config.dependencies import Container
from src.config.settings import Settings
from src.application.vehicle.services.vehicle_application_service import VehicleApplicationService
from src.application.user.services.user_application_service import UserApplicationService
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.domain.vehicle.value_objects import DecodeResult
from src.infrastructure.monitoring.logging_config import setup_logging

logger = logging.getLogger(__name__)


# Pydantic Models for API
class VINRequest(BaseModel):
    """VIN decode request."""
    vin: str = Field(..., min_length=17, max_length=17, description="Vehicle Identification Number")
    force_refresh: bool = Field(default=False, description="Force fresh decode even if cached")
    preferred_service: Optional[str] = Field(default="nhtsa", description="Preferred decoder service")


class VehicleResponse(BaseModel):
    """Vehicle response model."""
    id: Optional[str] = None
    vin: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vehicle_type: Optional[str] = None
    engine_info: Optional[str] = None
    fuel_type: Optional[str] = None
    decoded_at: str
    user_id: Optional[int] = None
    raw_data: Dict[str, Any] = {}
    
    @classmethod
    def from_decode_result(cls, result: DecodeResult, user_id: Optional[int] = None) -> "VehicleResponse":
        """Create from domain DecodeResult."""
        # Extract additional attributes from the attributes dict
        attrs = result.attributes or {}
        return cls(
            id=str(result.vehicle_id) if hasattr(result, 'vehicle_id') else None,
            vin=result.vin,
            manufacturer=result.manufacturer,
            model=result.model,
            year=result.model_year,
            vehicle_type=attrs.get('vehicle_type') or attrs.get('body_class'),
            engine_info=attrs.get('engine_model') or attrs.get('engine_configuration'),
            fuel_type=attrs.get('fuel_type') or attrs.get('fuel_type_primary'),
            decoded_at=datetime.utcnow().isoformat(),
            user_id=user_id,
            raw_data=result.raw_response or {}
        )


class StatsResponse(BaseModel):
    """Statistics response model."""
    total_vehicles: int = 0
    unique_manufacturers: int = 0
    recent_decodes: int = 0


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    database: str
    cache: str


# Dependency injection setup
container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting API server...")
    
    # Initialize settings
    settings = container.settings()
    setup_logging(settings.log_level)
    
    # Initialize database if configured
    try:
        await Container.initialize_database(container)
    except Exception as e:
        logger.warning(f"Database initialization failed, using in-memory: {e}")
    
    # Bootstrap command/query buses
    Container.bootstrap(container)
    
    # Wire dependencies
    container.wire(modules=[__name__])
    
    logger.info("API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API server...")
    
    # Close database connections
    if container.database_engine():
        engine = container.database_engine()
        if hasattr(engine, 'dispose'):
            await engine.dispose()
    
    logger.info("API server shut down")


# Create FastAPI app
app = FastAPI(
    title="VIN Decoder API",
    version="2.0.0",
    description="Domain-driven VIN decoder API with proper architecture",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Endpoints
@app.get("/health", response_model=HealthResponse)
@inject
async def health_check(
    settings: Settings = Depends(Provide[Container.settings])
) -> HealthResponse:
    """Health check endpoint."""
    # Check database status
    db_status = "unavailable"
    try:
        if container.database_engine():
            # Simple connectivity check
            engine = container.database_engine()
            async with engine.async_session_maker() as session:
                await session.execute("SELECT 1")
                db_status = "healthy"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        db_status = f"unhealthy: {str(e)[:50]}"
    
    # Check cache status
    cache_status = "unavailable"
    try:
        if container.upstash_cache():
            cache = container.upstash_cache()
            # Simple ping
            await cache.get("health_check")
            cache_status = "healthy"
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")
        cache_status = f"unhealthy: {str(e)[:50]}"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        database=db_status,
        cache=cache_status
    )


@app.post("/api/decode", response_model=Dict[str, Any])
@inject
async def decode_vin(
    request: VINRequest,
    vehicle_service: VehicleApplicationService = Depends(Provide[Container.vehicle_application_service]),
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> Dict[str, Any]:
    """Decode a VIN using the domain service."""
    try:
        # Create user preferences (in real app, get from authenticated user)
        preferences = UserPreferences(
            preferred_decoder=request.preferred_service or "nhtsa",
            language="en"
        )
        
        # Decode VIN using application service
        result = await vehicle_service.decode_vin(
            vin=request.vin,
            user_preferences=preferences,
            force_refresh=request.force_refresh
        )
        
        # Convert to response model
        vehicle = VehicleResponse.from_decode_result(result)
        
        return {
            "success": True,
            "vehicle": vehicle.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to decode VIN {request.vin}: {e}")
        raise HTTPException(status_code=500, detail="Failed to decode VIN")


@app.get("/api/vehicles", response_model=Dict[str, Any])
@inject
async def get_vehicles(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    vehicle_service: VehicleApplicationService = Depends(Provide[Container.vehicle_application_service]),
    vehicle_repo = Depends(Provide[Container.vehicle_repository])
) -> Dict[str, Any]:
    """Get decoded vehicles with pagination."""
    try:
        # Use the injected vehicle repository
        
        # Get all vehicles (pagination would need to be implemented in repository)
        all_vehicles = await vehicle_repo.find_all()
        
        # Calculate pagination
        total = len(all_vehicles)
        offset = (page - 1) * limit
        vehicles = all_vehicles[offset:offset + limit]
        
        # Convert to response models
        vehicle_responses = []
        for vehicle in vehicles:
            # Create response from Vehicle entity
            vehicle_responses.append({
                "id": str(vehicle.id),
                "vin": str(vehicle.vin.value),
                "manufacturer": vehicle.manufacturer,
                "model": vehicle.model,
                "year": vehicle.model_year,
                "vehicle_type": vehicle.vehicle_type,
                "engine_info": vehicle.engine_model,
                "fuel_type": vehicle.fuel_type,
                "decoded_at": vehicle.decoded_at.isoformat() if hasattr(vehicle, 'decoded_at') else datetime.utcnow().isoformat(),
                "user_id": vehicle.user_id if hasattr(vehicle, 'user_id') else None,
                "raw_data": vehicle.raw_data if hasattr(vehicle, 'raw_data') else {}
            })
        
        # Calculate total pages
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        
        return {
            "vehicles": vehicle_responses,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Failed to get vehicles: {e}")
        return {
            "vehicles": [],
            "page": page,
            "limit": limit,
            "total": 0,
            "total_pages": 0
        }


@app.get("/api/stats", response_model=StatsResponse)
@inject
async def get_stats(
    vehicle_service: VehicleApplicationService = Depends(Provide[Container.vehicle_application_service]),
    vehicle_repo = Depends(Provide[Container.vehicle_repository])
) -> StatsResponse:
    """Get application statistics."""
    try:
        # Use the injected vehicle repository
        
        # Get all vehicles for statistics
        all_vehicles = await vehicle_repo.find_all()
        total_vehicles = len(all_vehicles)
        
        # Get unique manufacturers
        manufacturers = set(v.manufacturer for v in all_vehicles if v.manufacturer)
        unique_manufacturers = len(manufacturers)
        
        # Recent decodes - for simplicity, take last 10 vehicles
        # In production, would filter by decoded_at timestamp
        recent_decodes = min(total_vehicles, 10)
        
        return StatsResponse(
            total_vehicles=total_vehicles,
            unique_manufacturers=unique_manufacturers,
            recent_decodes=recent_decodes
        )
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return StatsResponse()


@app.delete("/api/vehicles/{vehicle_id}")
@inject
async def delete_vehicle(
    vehicle_id: str,
    vehicle_service: VehicleApplicationService = Depends(Provide[Container.vehicle_application_service])
) -> Dict[str, bool]:
    """Delete a vehicle by ID."""
    try:
        vehicle_repo = container.vehicle_repository()
        
        # Delete vehicle from repository
        success = await vehicle_repo.delete(vehicle_id)
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Failed to delete vehicle {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete vehicle")


@app.get("/api/users/me")
@inject
async def get_current_user(
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> Dict[str, Any]:
    """Get current user information (mock for now)."""
    # In real app, get from authentication
    # For now, return mock user
    return {
        "id": 1,
        "telegram_id": 123456789,
        "username": "demo_user",
        "first_name": "Demo",
        "last_name": "User",
        "preferences": {
            "preferred_service": "nhtsa",
            "language_code": "en"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)