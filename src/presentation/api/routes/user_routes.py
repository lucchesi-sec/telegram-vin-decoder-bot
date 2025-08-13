"""User-related API routes following DDD principles."""

from fastapi import APIRouter, Depends, HTTPException
from src.application.user.services.user_application_service import UserApplicationService
from src.presentation.api.dependencies.container import get_user_service
from src.presentation.shared.dto.user_dto import UserResponseDTO
from src.presentation.shared.auth.jwt_handler import get_current_user_id


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponseDTO)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
):
    """Get current user information."""
    try:
        
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return UserResponseDTO.from_domain(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))