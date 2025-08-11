"""Upstash Redis cache implementation."""

import json
import logging
from typing import Optional, Any, Dict
from datetime import timedelta
from upstash_redis import Redis
from upstash_redis.errors import UpstashError


logger = logging.getLogger(__name__)


class UpstashCache:
    """Upstash Redis cache implementation."""
    
    def __init__(self, redis_url: str, redis_token: str):
        """Initialize Upstash cache.
        
        Args:
            redis_url: Upstash Redis REST URL
            redis_token: Upstash Redis REST token
        """
        self.redis = Redis(url=redis_url, token=redis_token)
        self.default_ttl = 86400 * 30  # 30 days default
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.redis.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(value) if isinstance(value, str) else value
            logger.debug(f"Cache miss for key: {key}")
            return None
        except UpstashError as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            self.redis.setex(key, ttl, serialized)
            logger.debug(f"Cached key: {key} with TTL: {ttl}")
            return True
        except UpstashError as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = self.redis.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return bool(result)
        except UpstashError as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists, False otherwise
        """
        try:
            return bool(self.redis.exists(key))
        except UpstashError as e:
            logger.error(f"Error checking cache existence: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value or None on error
        """
        try:
            return self.redis.incrby(key, amount)
        except UpstashError as e:
            logger.error(f"Error incrementing cache: {e}")
            return None
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for a key.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return bool(self.redis.expire(key, ttl))
        except UpstashError as e:
            logger.error(f"Error setting expiration: {e}")
            return False
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for a key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds or None if key doesn't exist or no TTL
        """
        try:
            ttl = self.redis.ttl(key)
            return ttl if ttl > 0 else None
        except UpstashError as e:
            logger.error(f"Error getting TTL: {e}")
            return None


class CacheKeys:
    """Cache key patterns."""
    
    @staticmethod
    def vin(vin: str) -> str:
        """Generate cache key for VIN data."""
        return f"vin:{vin}"
    
    @staticmethod
    def user_rate_limit(telegram_id: int) -> str:
        """Generate cache key for user rate limiting."""
        return f"rate:{telegram_id}"
    
    @staticmethod
    def user_session(telegram_id: int) -> str:
        """Generate cache key for user session."""
        return f"session:{telegram_id}"
    
    @staticmethod
    def bulk_job(job_id: str) -> str:
        """Generate cache key for bulk job status."""
        return f"job:{job_id}"
    
    @staticmethod
    def user_preferences(telegram_id: int) -> str:
        """Generate cache key for user preferences."""
        return f"prefs:{telegram_id}"