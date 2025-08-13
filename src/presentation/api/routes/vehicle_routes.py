"""Vehicle-related API routes following DDD principles."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.application.vehicle.services.vehicle_application_service import VehicleApplicationService
from src.presentation.api.dependencies.container import get_vehicle_service
from src.presentation.shared.dto.vehicle_dto import VehicleResponseDTO, VehicleDecodeRequestDTO, VehicleDecodeResponseDTO
from src.presentation.shared.auth.jwt_handler import get_current_user_id, get_optional_user_id


router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("", response_model=dict)
async def get_vehicles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    vehicle_service: VehicleApplicationService = Depends(get_vehicle_service)
):
    """Get paginated list of vehicles for the current user."""
    try:
        
        vehicles = await vehicle_service.get_user_vehicles(user_id, page, limit)
        
        return {
            "vehicles": [VehicleResponseDTO.from_domain(vehicle) for vehicle in vehicles],
            "page": page,
            "limit": limit,
            "total_pages": 1  # TODO: Implement proper pagination in repository
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decode", response_model=VehicleDecodeResponseDTO)
async def decode_vin(
    request: VehicleDecodeRequestDTO,
    user_id: int = Depends(get_current_user_id),
    vehicle_service: VehicleApplicationService = Depends(get_vehicle_service)
):
    """Decode a VIN using the domain service."""
    try:
        
        vehicle = await vehicle_service.decode_vin(request.vin, user_id)
        
        return VehicleDecodeResponseDTO(
            success=True,
            vehicle=VehicleResponseDTO.from_domain(vehicle)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    user_id: int = Depends(get_current_user_id),
    vehicle_service: VehicleApplicationService = Depends(get_vehicle_service)
):
    """Delete a vehicle by ID."""
    try:
        
        await vehicle_service.delete_vehicle(vehicle_id, user_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))