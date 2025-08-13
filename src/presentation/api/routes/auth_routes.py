"""Authentication routes for unified auth system."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src.application.user.services.user_application_service import UserApplicationService
from src.presentation.api.dependencies.container import get_user_service
from src.presentation.shared.auth.jwt_handler import JWTHandler, get_current_user_id
from src.presentation.shared.dto.user_dto import UserResponseDTO


router = APIRouter(prefix="/api/auth", tags=["authentication"])


class TelegramAuthRequest(BaseModel):
    """Request model for Telegram authentication."""
    telegram_id: int
    username: str = None
    first_name: str = None
    last_name: str = None


class AuthResponse(BaseModel):
    """Response model for authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponseDTO


@router.post("/telegram", response_model=AuthResponse)
async def authenticate_telegram_user(
    request: TelegramAuthRequest,
    user_service: UserApplicationService = Depends(get_user_service)
):
    """Authenticate a Telegram user and return JWT token."""
    try:
        # Get or create user through domain service
        user = await user_service.get_or_create_user(
            telegram_id=request.telegram_id,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name
        )
        
        # Create JWT token
        access_token = JWTHandler.create_access_token(
            user_id=user.id.value,
            telegram_id=user.telegram_id.value
        )
        
        return AuthResponse(
            access_token=access_token,
            user=UserResponseDTO.from_domain(user)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.post("/refresh")
async def refresh_token(
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
):
    """Refresh an existing JWT token."""
    try:
        user = await user_service.get_user(current_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create new JWT token
        access_token = JWTHandler.create_access_token(
            user_id=user.id.value,
            telegram_id=user.telegram_id.value
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")