"""User preferences service for managing user settings and data."""

import logging
from typing import Optional, Dict, Any, List
from telegram.ext import ContextTypes

from .base import Service
from ..user_data import UserDataManager


class UserPreferencesService(Service):
    """Service for managing user preferences and settings."""
    
    async def get_user_settings(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Get user settings.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dictionary of user settings
        """
        user_data_mgr = self.get_dependency('user_data_manager')
        if not user_data_mgr:
            return {}
        
        return await user_data_mgr.get_user_settings(user_id)
    
    async def update_user_service(
        self,
        user_id: int,
        service: str
    ) -> bool:
        """Update user's preferred service.
        
        Args:
            user_id: The user ID
            service: The service name (NHTSA or AutoDev)
            
        Returns:
            True if successful
        """
        user_data_mgr = self.get_dependency('user_data_manager')
        if not user_data_mgr:
            return False
        
        return await user_data_mgr.set_user_service(user_id, service)
    
    async def save_api_key(
        self,
        user_id: int,
        service: str,
        api_key: str
    ) -> bool:
        """Save an API key for a user.
        
        Args:
            user_id: The user ID
            service: The service name
            api_key: The API key to save
            
        Returns:
            True if successful
        """
        user_data_mgr = self.get_dependency('user_data_manager')
        if not user_data_mgr:
            return False
        
        return await user_data_mgr.set_user_api_key(user_id, service, api_key)
    
    async def clear_api_key(
        self,
        user_id: int,
        service: str
    ) -> bool:
        """Clear an API key for a user.
        
        Args:
            user_id: The user ID
            service: The service name
            
        Returns:
            True if successful
        """
        user_data_mgr = self.get_dependency('user_data_manager')
        if not user_data_mgr:
            return False
        
        return await user_data_mgr.clear_user_api_key(user_id, service)
    
    async def get_history(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get user's VIN search history.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of VIN history entries
        """
        user_data_mgr = self.get_dependency('user_data_manager')
        if not user_data_mgr:
            return []
        
        return await user_data_mgr.get_history(user_id)
    
    async def get_favorites(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get user's favorite vehicles.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of favorite vehicles
        """
        user_data_mgr = self.get_dependency('user_data_manager')
        if not user_data_mgr:
            return []
        
        return await user_data_mgr.get_favorites(user_id)
    
    async def add_to_favorites(
        self,
        user_id: int,
        vin: str,
        vehicle_data: Dict[str, Any]
    ) -> bool:
        """Add a vehicle to user's favorites.
        
        Args:
            user_id: The user ID
            vin: The VIN
            vehicle_data: The vehicle data
            
        Returns:
            True if successful
        """
        user_data_mgr = self.get_dependency('user_data_manager')
        if not user_data_mgr:
            return False
        
        return await user_data_mgr.add_to_favorites(user_id, vin, vehicle_data)
    
    async def remove_from_favorites(
        self,
        user_id: int,
        vin: str
    ) -> bool:
        """Remove a vehicle from user's favorites.
        
        Args:
            user_id: The user ID
            vin: The VIN
            
        Returns:
            True if successful
        """
        user_data_mgr = self.get_dependency('user_data_manager')
        if not user_data_mgr:
            return False
        
        return await user_data_mgr.remove_from_favorites(user_id, vin)
    
    async def validate_api_key(
        self,
        service: str,
        api_key: str
    ) -> bool:
        """Validate an API key for a service.
        
        Args:
            service: The service name
            api_key: The API key to validate
            
        Returns:
            True if valid
        """
        if service == "AutoDev":
            from ..autodev_client import AutoDevClient
            client = AutoDevClient(api_key=api_key)
            return client.validate_api_key(api_key)
        
        # Other services don't require validation
        return True