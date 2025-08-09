from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

import redis

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self, redis_url: Optional[str] = None, ttl_seconds: int = 86400):
        """
        Initialize Redis cache for VIN lookups.
        
        Args:
            redis_url: Redis connection URL. If None, will look for REDIS_URL env var.
            ttl_seconds: Time-to-live for cached entries in seconds (default: 24 hours)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.ttl_seconds = ttl_seconds
        self._client: Optional[redis.Redis] = None
        self.enabled = bool(self.redis_url)
        
        if not self.enabled:
            logger.info("Redis caching disabled (no REDIS_URL configured)")
        else:
            logger.info(f"Redis caching enabled with TTL={ttl_seconds}s")
    
    def _get_client(self) -> Optional[redis.Redis]:
        """Get or create Redis client."""
        if not self.enabled:
            return None
            
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self._client.ping()
                logger.info("Connected to Redis successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.enabled = False
                return None
                
        return self._client
    
    def _make_key(self, vin: str) -> str:
        """Create cache key for a VIN."""
        return f"vin:{vin.upper()}"
    
    async def get(self, vin: str) -> Optional[Dict[str, Any]]:
        """
        Get cached VIN data.
        
        Args:
            vin: Vehicle identification number
            
        Returns:
            Cached data if available, None otherwise
        """
        if not self.enabled:
            return None
            
        client = self._get_client()
        if not client:
            return None
            
        try:
            key = self._make_key(vin)
            data = client.get(key)
            
            if data:
                logger.info(f"Cache hit for VIN: {vin}")
                return json.loads(data)
            else:
                logger.info(f"Cache miss for VIN: {vin}")
                return None
                
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, vin: str, data: Dict[str, Any]) -> bool:
        """
        Cache VIN data.
        
        Args:
            vin: Vehicle identification number
            data: Data to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled:
            return False
            
        client = self._get_client()
        if not client:
            return False
            
        try:
            key = self._make_key(vin)
            json_data = json.dumps(data)
            client.setex(key, self.ttl_seconds, json_data)
            logger.info(f"Cached data for VIN: {vin}")
            return True
            
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._client = None