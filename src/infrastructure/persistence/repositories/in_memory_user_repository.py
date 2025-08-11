"""In-memory user repository implementation."""

import logging
from typing import Optional, List, Dict
from src.domain.user.entities.user import User
from src.domain.user.repositories.user_repository import UserRepository
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of user repository for testing and development."""
    
    def __init__(self):
        """Initialize the in-memory repository."""
        self._users: Dict[str, User] = {}
        self._telegram_id_index: Dict[int, str] = {}
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by internal ID.
        
        Args:
            user_id: Internal user ID
            
        Returns:
            User if found, None otherwise
        """
        return self._users.get(user_id)
    
    async def get_by_telegram_id(self, telegram_id: TelegramID) -> Optional[User]:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User if found, None otherwise
        """
        user_id = self._telegram_id_index.get(telegram_id.value)
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def save(self, user: User) -> None:
        """Save or update a user.
        
        Args:
            user: User to save
        """
        self._users[user.id] = user
        self._telegram_id_index[user.telegram_id.value] = user.id
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: Internal user ID
            
        Returns:
            True if deleted, False if not found
        """
        user = self._users.get(user_id)
        if user:
            del self._users[user_id]
            del self._telegram_id_index[user.telegram_id.value]
            return True
        return False
    
    async def list_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List active users.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of active users
        """
        active_users = [u for u in self._users.values() if u.is_active]
        return active_users[offset:offset + limit]
    
    async def exists_by_telegram_id(self, telegram_id: TelegramID) -> bool:
        """Check if user exists by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            True if user exists, False otherwise
        """
        return telegram_id.value in self._telegram_id_index
    
    async def count_active_users(self) -> int:
        """Count active users.
        
        Returns:
            Number of active users
        """
        return sum(1 for u in self._users.values() if u.is_active)
    
    async def find_all(self) -> List[User]:
        """Find all users.
        
        Returns:
            List of all users
        """
        return list(self._users.values())
    
    def clear(self) -> None:
        """Clear all users from the repository (for testing)."""
        self._users.clear()
        self._telegram_id_index.clear()