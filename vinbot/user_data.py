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
    
    def _get_history_key(self, user_id: int) -> str:
        """Get cache key for user's history"""
        return f"user:{user_id}:history"
    
    def _get_favorites_key(self, user_id: int) -> str:
        """Get cache key for user's favorites"""
        return f"user:{user_id}:favorites"
    
    def _get_vehicle_data_key(self, vin: str) -> str:
        """Get cache key for vehicle data"""
        return f"vehicle:{vin}"
    
    async def add_to_history(self, user_id: int, vin: str, vehicle_data: Dict[str, Any]) -> bool:
        """Add a VIN to user's search history"""
        if not self.cache:
            return False
        
        try:
            # Store vehicle data separately for quick access
            vehicle_key = self._get_vehicle_data_key(vin)
            await self.cache.set(vehicle_key, json.dumps(vehicle_data), ttl=self.history_ttl)
            
            # Get current history
            history_key = self._get_history_key(user_id)
            history_json = await self.cache.get(history_key)
            
            if history_json:
                history = json.loads(history_json)
            else:
                history = []
            
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
            await self.cache.set(history_key, json.dumps(history), ttl=self.history_ttl)
            
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
        if not self.cache:
            return []
        
        try:
            history_key = self._get_history_key(user_id)
            history_json = await self.cache.get(history_key)
            
            if not history_json:
                return []
            
            history = json.loads(history_json)
            
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
        if not self.cache:
            return False
        
        try:
            # Store vehicle data
            vehicle_key = self._get_vehicle_data_key(vin)
            await self.cache.set(vehicle_key, json.dumps(vehicle_data), ttl=self.favorites_ttl)
            
            # Get current favorites
            favorites_key = self._get_favorites_key(user_id)
            favorites_json = await self.cache.get(favorites_key)
            
            if favorites_json:
                favorites = json.loads(favorites_json)
            else:
                favorites = []
            
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
            await self.cache.set(favorites_key, json.dumps(favorites), ttl=self.favorites_ttl)
            
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
        if not self.cache:
            return []
        
        try:
            favorites_key = self._get_favorites_key(user_id)
            favorites_json = await self.cache.get(favorites_key)
            
            if not favorites_json:
                return []
            
            favorites = json.loads(favorites_json)
            
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
        if not self.cache:
            return False
        
        try:
            favorites_key = self._get_favorites_key(user_id)
            favorites_json = await self.cache.get(favorites_key)
            
            if not favorites_json:
                return False
            
            favorites = json.loads(favorites_json)
            
            # Remove the VIN
            original_len = len(favorites)
            favorites = [f for f in favorites if f.get("vin") != vin]
            
            if len(favorites) < original_len:
                # Save updated list
                await self.cache.set(favorites_key, json.dumps(favorites), ttl=self.favorites_ttl)
                logger.info(f"Removed VIN {vin} from favorites for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing from favorites: {e}")
            return False
    
    async def get_vehicle_data(self, vin: str) -> Optional[Dict[str, Any]]:
        """Get cached vehicle data by VIN"""
        if not self.cache:
            return None
        
        try:
            vehicle_key = self._get_vehicle_data_key(vin)
            data_json = await self.cache.get(vehicle_key)
            
            if data_json:
                return json.loads(data_json)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting vehicle data: {e}")
            return None
    
    async def clear_user_history(self, user_id: int) -> bool:
        """Clear user's search history"""
        if not self.cache:
            return False
        
        try:
            history_key = self._get_history_key(user_id)
            # Set to empty list rather than deleting
            await self.cache.set(history_key, json.dumps([]), ttl=self.history_ttl)
            logger.info(f"Cleared history for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False
    
    async def update_favorite_nickname(self, user_id: int, vin: str, new_nickname: str) -> bool:
        """Update the nickname for a saved vehicle"""
        if not self.cache:
            return False
        
        try:
            favorites_key = self._get_favorites_key(user_id)
            favorites_json = await self.cache.get(favorites_key)
            
            if not favorites_json:
                return False
            
            favorites = json.loads(favorites_json)
            
            # Find and update the entry
            updated = False
            for entry in favorites:
                if entry.get("vin") == vin:
                    entry["nickname"] = new_nickname
                    updated = True
                    break
            
            if updated:
                await self.cache.set(favorites_key, json.dumps(favorites), ttl=self.favorites_ttl)
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