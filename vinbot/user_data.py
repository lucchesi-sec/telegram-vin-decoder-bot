import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class UserDataManager:
    """Manages user-specific data like history and favorites using cache backend"""
    
    def __init__(self, cache=None):
        """Initialize with optional cache backend (Redis/Upstash)"""
        self.cache = cache
        self.history_limit = 10  # Max recent searches per user
        self.favorites_limit = 20  # Max saved vehicles per user
        self.history_ttl = 30 * 24 * 3600  # 30 days for history
        self.favorites_ttl = 365 * 24 * 3600  # 1 year for favorites
        
        # In-memory fallback storage when no cache is configured
        self._in_memory_storage = {}
    
    def _get_history_key(self, user_id: int) -> str:
        """Get cache key for user's history"""
        return f"user:{user_id}:history"
    
    def _get_favorites_key(self, user_id: int) -> str:
        """Get cache key for user's favorites"""
        return f"user:{user_id}:favorites"
    
    def _get_vehicle_data_key(self, vin: str) -> str:
        """Get cache key for vehicle data"""
        return f"vehicle:{vin}"
    
    def _get_settings_key(self, user_id: int) -> str:
        """Get cache key for user's settings"""
        return f"user:{user_id}:settings"
    
    async def add_to_history(self, user_id: int, vin: str, vehicle_data: Dict[str, Any]) -> bool:
        """Add a VIN to user's search history"""
        try:
            # Store vehicle data separately for quick access
            vehicle_key = self._get_vehicle_data_key(vin)
            if self.cache:
                await self.cache.set(vehicle_key, json.dumps(vehicle_data), ttl=self.history_ttl)
            else:
                # In-memory fallback
                self._in_memory_storage[vehicle_key] = {
                    "data": vehicle_data,
                    "timestamp": datetime.now(),
                    "ttl": self.history_ttl
                }
            
            # Get current history
            history_key = self._get_history_key(user_id)
            if self.cache:
                history_json = await self.cache.get(history_key)
                if history_json:
                    history = json.loads(history_json)
                else:
                    history = []
            else:
                # In-memory fallback
                history_data = self._in_memory_storage.get(history_key, {})
                history = history_data.get("data", []) if history_data else []
            
            # Extract vehicle info for display
            attrs = vehicle_data.get("attributes", {})
            make_model = f"{attrs.get('year', '')} {attrs.get('make', '')} {attrs.get('model', '')}".strip()
            
            # Create history entry
            entry = {
                "vin": vin,
                "make_model": make_model,
                "timestamp": datetime.now().isoformat()
            }
            
            # Remove duplicates (same VIN)
            history = [h for h in history if h.get("vin") != vin]
            
            # Add to beginning
            history.insert(0, entry)
            
            # Limit history size
            history = history[:self.history_limit]
            
            # Save back to cache
            if self.cache:
                await self.cache.set(history_key, json.dumps(history), ttl=self.history_ttl)
            else:
                # In-memory fallback
                self._in_memory_storage[history_key] = {
                    "data": history,
                    "timestamp": datetime.now(),
                    "ttl": self.history_ttl
                }
            
            logger.info(f"Added VIN {vin} to history for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding to history: {e}")
            return False
    
    async def get_history(self, user_id: int) -> List[Tuple[str, str, str]]:
        """Get user's search history
        
        Returns:
            List of tuples (vin, make_model, timestamp)
        """
        try:
            history_key = self._get_history_key(user_id)
            if self.cache:
                history_json = await self.cache.get(history_key)
                if not history_json:
                    return []
                history = json.loads(history_json)
            else:
                # In-memory fallback
                history_data = self._in_memory_storage.get(history_key, {})
                history = history_data.get("data", []) if history_data else []
            
            # Convert to tuples for display
            result = []
            for entry in history:
                result.append((
                    entry.get("vin", ""),
                    entry.get("make_model", ""),
                    entry.get("timestamp", "")
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
    async def add_to_favorites(self, user_id: int, vin: str, vehicle_data: Dict[str, Any], nickname: Optional[str] = None) -> bool:
        """Add a vehicle to user's favorites"""
        try:
            # Store vehicle data
            vehicle_key = self._get_vehicle_data_key(vin)
            if self.cache:
                await self.cache.set(vehicle_key, json.dumps(vehicle_data), ttl=self.favorites_ttl)
            else:
                # In-memory fallback
                self._in_memory_storage[vehicle_key] = {
                    "data": vehicle_data,
                    "timestamp": datetime.now(),
                    "ttl": self.favorites_ttl
                }
            
            # Get current favorites
            favorites_key = self._get_favorites_key(user_id)
            if self.cache:
                favorites_json = await self.cache.get(favorites_key)
                if favorites_json:
                    favorites = json.loads(favorites_json)
                else:
                    favorites = []
            else:
                # In-memory fallback
                favorites_data = self._in_memory_storage.get(favorites_key, {})
                favorites = favorites_data.get("data", []) if favorites_data else []
            
            # Extract vehicle info
            attrs = vehicle_data.get("attributes", {})
            make_model = f"{attrs.get('year', '')} {attrs.get('make', '')} {attrs.get('model', '')}".strip()
            
            # Create favorite entry
            entry = {
                "vin": vin,
                "nickname": nickname or make_model,
                "make_model": make_model,
                "timestamp": datetime.now().isoformat()
            }
            
            # Remove duplicates
            favorites = [f for f in favorites if f.get("vin") != vin]
            
            # Add new favorite
            favorites.append(entry)
            
            # Limit favorites size
            if len(favorites) > self.favorites_limit:
                favorites = favorites[-self.favorites_limit:]  # Keep most recent
            
            # Save back to cache
            if self.cache:
                await self.cache.set(favorites_key, json.dumps(favorites), ttl=self.favorites_ttl)
            else:
                # In-memory fallback
                self._in_memory_storage[favorites_key] = {
                    "data": favorites,
                    "timestamp": datetime.now(),
                    "ttl": self.favorites_ttl
                }
            
            logger.info(f"Added VIN {vin} to favorites for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding to favorites: {e}")
            return False
    
    async def get_favorites(self, user_id: int) -> List[Tuple[str, str, str]]:
        """Get user's saved vehicles
        
        Returns:
            List of tuples (vin, nickname, make_model)
        """
        try:
            favorites_key = self._get_favorites_key(user_id)
            if self.cache:
                favorites_json = await self.cache.get(favorites_key)
                if not favorites_json:
                    return []
                favorites = json.loads(favorites_json)
            else:
                # In-memory fallback
                favorites_data = self._in_memory_storage.get(favorites_key, {})
                favorites = favorites_data.get("data", []) if favorites_data else []
            
            # Convert to tuples
            result = []
            for entry in favorites:
                result.append((
                    entry.get("vin", ""),
                    entry.get("nickname", ""),
                    entry.get("make_model", "")
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting favorites: {e}")
            return []
    
    async def remove_from_favorites(self, user_id: int, vin: str) -> bool:
        """Remove a vehicle from user's favorites"""
        try:
            favorites_key = self._get_favorites_key(user_id)
            if self.cache:
                favorites_json = await self.cache.get(favorites_key)
                if not favorites_json:
                    return False
                favorites = json.loads(favorites_json)
            else:
                # In-memory fallback
                favorites_data = self._in_memory_storage.get(favorites_key, {})
                favorites = favorites_data.get("data", []) if favorites_data else []
                if not favorites:
                    return False
            
            # Remove the VIN
            original_len = len(favorites)
            favorites = [f for f in favorites if f.get("vin") != vin]
            
            if len(favorites) < original_len:
                # Save updated list
                if self.cache:
                    await self.cache.set(favorites_key, json.dumps(favorites), ttl=self.favorites_ttl)
                else:
                    # In-memory fallback
                    self._in_memory_storage[favorites_key] = {
                        "data": favorites,
                        "timestamp": datetime.now(),
                        "ttl": self.favorites_ttl
                    }
                logger.info(f"Removed VIN {vin} from favorites for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing from favorites: {e}")
            return False
    
    async def get_vehicle_data(self, vin: str) -> Optional[Dict[str, Any]]:
        """Get cached vehicle data by VIN"""
        try:
            vehicle_key = self._get_vehicle_data_key(vin)
            if self.cache:
                data_json = await self.cache.get(vehicle_key)
                if data_json:
                    return json.loads(data_json)
                return None
            else:
                # In-memory fallback
                vehicle_data = self._in_memory_storage.get(vehicle_key, {})
                return vehicle_data.get("data") if vehicle_data else None
            
        except Exception as e:
            logger.error(f"Error getting vehicle data: {e}")
            return None
    
    async def clear_user_history(self, user_id: int) -> bool:
        """Clear user's search history"""
        try:
            history_key = self._get_history_key(user_id)
            # Set to empty list rather than deleting
            if self.cache:
                await self.cache.set(history_key, json.dumps([]), ttl=self.history_ttl)
            else:
                # In-memory fallback
                self._in_memory_storage[history_key] = {
                    "data": [],
                    "timestamp": datetime.now(),
                    "ttl": self.history_ttl
                }
            logger.info(f"Cleared history for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False
    
    async def update_favorite_nickname(self, user_id: int, vin: str, new_nickname: str) -> bool:
        """Update the nickname for a saved vehicle"""
        try:
            favorites_key = self._get_favorites_key(user_id)
            if self.cache:
                favorites_json = await self.cache.get(favorites_key)
                if not favorites_json:
                    return False
                favorites = json.loads(favorites_json)
            else:
 
               # In-memory fallback
                favorites_data = self._in_memory_storage.get(favorites_key, {})
                favorites = favorites_data.get("data", []) if favorites_data else []
                if not favorites:
                    return False
            
            # Find and update the entry
            updated = False
            for entry in favorites:
                if entry.get("vin") == vin:
                    entry["nickname"] = new_nickname
                    updated = True
                    break
            
            if updated:
                if self.cache:
                    await self.cache.set(favorites_key, json.dumps(favorites), ttl=self.favorites_ttl)
                else:
                    # In-memory fallback
                    self._in_memory_storage[favorites_key] = {
                        "data": favorites,
                        "timestamp": datetime.now(),
                        "ttl": self.favorites_ttl
                    }
                logger.info(f"Updated nickname for VIN {vin} for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating nickname: {e}")
            return False
    
    async def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """Get user statistics"""
        history = await self.get_history(user_id)
        favorites = await self.get_favorites(user_id)
        
        return {
            "total_searches": len(history),
            "saved_vehicles": len(favorites)
        }
    
    async def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user's settings including preferred service and API keys
        
        Returns:
            Dictionary with service preference and API keys
        """
        try:
            settings_key = self._get_settings_key(user_id)
            if self.cache:
                settings_json = await self.cache.get(settings_key)
                if settings_json:
                    settings = json.loads(settings_json)
                else:
                    settings = None
            else:
                # In-memory fallback
                settings_data = self._in_memory_storage.get(settings_key, {})
                settings = settings_data.get("data") if settings_data else None
            
            if settings:
                # Ensure all expected keys exist
                if "service" not in settings:
                    settings["service"] = "NHTSA"  # Changed default to NHTSA
                if "carsxe_api_key" not in settings:
                    settings["carsxe_api_key"] = None
                if "nhtsa_api_key" not in settings:
                    settings["nhtsa_api_key"] = None
                if "autodev_api_key" not in settings:
                    settings["autodev_api_key"] = None
                return settings
            
            # Return defaults if no settings exist
            return {
                "service": "NHTSA",
                "carsxe_api_key": None,
                "nhtsa_api_key": None,
                "autodev_api_key": None
            }
            
        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return {
                "service": "NHTSA",
                "carsxe_api_key": None,
                "nhtsa_api_key": None,
                "autodev_api_key": None
            }
    
    async def set_user_service(self, user_id: int, service: str) -> bool:
        """Set user's preferred VIN decoding service
        
        Args:
            user_id: User ID
            service: Service name (CarsXE, NHTSA, or AutoDev)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current settings
            settings = await self.get_user_settings(user_id)
            
            # Update service preference
            settings["service"] = service
            
            # Save back to cache
            settings_key = self._get_settings_key(user_id)
            settings_ttl = 365 * 24 * 3600  # 1 year
            if self.cache:
                await self.cache.set(settings_key, json.dumps(settings), ttl=settings_ttl)
            else:
                # In-memory fallback
                self._in_memory_storage[settings_key] = {
                    "data": settings,
                    "timestamp": datetime.now(),
                    "ttl": settings_ttl
                }
            
            logger.info(f"Updated service preference to {service} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting user service: {e}")
            return False
    
    async def set_user_api_key(self, user_id: int, service: str, api_key: Optional[str]) -> bool:
        """Set user's API key for a specific service
        
        Args:
            user_id: User ID
            service: Service name (CarsXE, NHTSA, or AutoDev)
            api_key: API key to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current settings
            settings = await self.get_user_settings(user_id)
            
            # Update API key for the specified service
            if service.lower() == "carsxe":
                settings["carsxe_api_key"] = api_key
            elif service.lower() == "nhtsa":
                settings["nhtsa_api_key"] = api_key  # NHTSA doesn't need key but keeping for consistency
            elif service.lower() == "autodev":
                settings["autodev_api_key"] = api_key
            else:
                logger.error(f"Unknown service: {service}")
                return False
            
            # Save back to cache
            settings_key = self._get_settings_key(user_id)
            settings_ttl = 365 * 24 * 3600  # 1 year
            if self.cache:
                await self.cache.set(settings_key, json.dumps(settings), ttl=settings_ttl)
            else:
                # In-memory fallback
                self._in_memory_storage[settings_key] = {
                    "data": settings,
                    "timestamp": datetime.now(),
                    "ttl": settings_ttl
                }
            
            logger.info(f"Updated API key for {service} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting API key: {e}")
            return False
    
    async def clear_user_api_key(self, user_id: int, service: str) -> bool:
        """Clear user's API key for a specific service
        
        Args:
            user_id: User ID
            service: Service name (CarsXE or NHTSA)
            
        Returns:
            True if successful, False otherwise
        """
        return await self.set_user_api_key(user_id, service, None)