"""User DTOs for API responses following DDD principles."""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from src.domain.user.entities.user import User


class UserResponseDTO(BaseModel):
    """Response DTO for user data."""
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    preferences: Optional[Dict[str, Any]] = None

    @classmethod
    def from_domain(cls, user: User) -> "UserResponseDTO":
        """Convert domain User entity to DTO."""
        return cls(
            id=user.id.value,
            telegram_id=user.telegram_id.value,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            created_at=user.created_at,
            preferences=user.preferences.to_dict() if user.preferences else {}
        )