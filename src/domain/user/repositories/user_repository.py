"""User repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.user.entities.user import User
from src.domain.user.value_objects.telegram_id import TelegramID


class UserRepository(ABC):
    """Abstract base class for user repository."""
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by internal ID.
        
        Args:
            user_id: Internal user ID
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: TelegramID) -> Optional[User]:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def save(self, user: User) -> None:
        """Save or update a user.
        
        Args:
            user: User to save
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: Internal user ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def list_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List active users.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of active users
        """
        pass
    
    @abstractmethod
    async def exists_by_telegram_id(self, telegram_id: TelegramID) -> bool:
        """Check if user exists by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            True if user exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def count_active_users(self) -> int:
        """Count active users.
        
        Returns:
            Number of active users
        """
        pass
    
    @abstractmethod
    async def find_all(self) -> List[User]:
        """Find all users (for backward compatibility).
        
        Returns:
            List of all users
        """
        pass