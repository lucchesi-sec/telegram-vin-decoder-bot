"""Cache repository for VIN data."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from src.domain.vehicle.entities.vehicle import Vehicle
from src.domain.vehicle.value_objects import VINNumber
from .upstash_cache import UpstashCache, CacheKeys


logger = logging.getLogger(__name__)


class VehicleCacheRepository:
    """Repository for caching vehicle data."""
    
    def __init__(self, cache: UpstashCache):
        """Initialize cache repository.
        
        Args:
            cache: Upstash cache instance
        """
        self.cache = cache
        self.default_ttl = 86400 * 30  # 30 days
    
    async def get_vehicle(self, vin: VINNumber) -> Optional[Dict[str, Any]]:
        """Get vehicle data from cache.
        
        Args:
            vin: Vehicle VIN number
            
        Returns:
            Cached vehicle data or None
        """
        key = CacheKeys.vin(vin.value)
        data = await self.cache.get(key)
        
        if data:
            logger.info(f"Cache hit for VIN: {vin.value}")
            # Check if cache is expired based on cached timestamp
            if 'cached_at' in data:
                cached_at = datetime.fromisoformat(data['cached_at'])
                if datetime.now() - cached_at > timedelta(days=30):
                    logger.info(f"Cache expired for VIN: {vin.value}")
                    await self.cache.delete(key)
                    return None
        
        return data
    
    async def cache_vehicle(
        self,
        vin: VINNumber,
        vehicle_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache vehicle data.
        
        Args:
            vin: Vehicle VIN number
            vehicle_data: Vehicle data to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = CacheKeys.vin(vin.value)
        
        # Add caching metadata
        vehicle_data['cached_at'] = datetime.now().isoformat()
        
        success = await self.cache.set(key, vehicle_data, ttl or self.default_ttl)
        
        if success:
            logger.info(f"Cached VIN data: {vin.value}")
        
        return success
    
    async def invalidate_vehicle(self, vin: VINNumber) -> bool:
        """Invalidate cached vehicle data.
        
        Args:
            vin: Vehicle VIN number
            
        Returns:
            True if deleted
        """
        key = CacheKeys.vin(vin.value)
        success = await self.cache.delete(key)
        
        if success:
            logger.info(f"Invalidated cache for VIN: {vin.value}")
        
        return success
    
    async def check_rate_limit(
        self,
        telegram_id: int,
        limit: int = 100,
        window: int = 60
    ) -> tuple[bool, int]:
        """Check and update rate limit for user.
        
        Args:
            telegram_id: User's Telegram ID
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, current_count)
        """
        key = CacheKeys.user_rate_limit(telegram_id)
        
        # Increment counter
        count = await self.cache.increment(key)
        
        if count == 1:
            # First request in window, set expiration
            await self.cache.expire(key, window)
        
        is_allowed = count <= limit
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for user {telegram_id}: {count}/{limit}")
        
        return is_allowed, count
    
    async def get_remaining_rate_limit(self, telegram_id: int) -> Optional[int]:
        """Get remaining time in rate limit window.
        
        Args:
            telegram_id: User's Telegram ID
            
        Returns:
            Remaining seconds or None
        """
        key = CacheKeys.user_rate_limit(telegram_id)
        return await self.cache.get_ttl(key)
    
    async def cache_user_session(
        self,
        telegram_id: int,
        session_data: Dict[str, Any],
        ttl: int = 3600
    ) -> bool:
        """Cache user session data.
        
        Args:
            telegram_id: User's Telegram ID
            session_data: Session data to cache
            ttl: Time to live in seconds (default 1 hour)
            
        Returns:
            True if successful
        """
        key = CacheKeys.user_session(telegram_id)
        return await self.cache.set(key, session_data, ttl)
    
    async def get_user_session(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user session data.
        
        Args:
            telegram_id: User's Telegram ID
            
        Returns:
            Session data or None
        """
        key = CacheKeys.user_session(telegram_id)
        return await self.cache.get(key)
    
    async def clear_user_session(self, telegram_id: int) -> bool:
        """Clear user session data.
        
        Args:
            telegram_id: User's Telegram ID
            
        Returns:
            True if deleted
        """
        key = CacheKeys.user_session(telegram_id)
        return await self.cache.delete(key)