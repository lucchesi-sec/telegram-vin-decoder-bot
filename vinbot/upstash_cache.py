from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional
import aiohttp

logger = logging.getLogger(__name__)


class UpstashCache:
    def __init__(self, rest_url: Optional[str] = None, rest_token: Optional[str] = None, ttl_seconds: int = 86400):
        """
        Initialize Upstash Redis cache for VIN lookups.
        
        Args:
            rest_url: Upstash REST URL. If None, will look for UPSTASH_REDIS_REST_URL env var.
            rest_token: Upstash REST token. If None, will look for UPSTASH_REDIS_REST_TOKEN env var.
            ttl_seconds: Time-to-live for cached entries in seconds (default: 24 hours)
        """
        self.rest_url = rest_url or os.getenv("UPSTASH_REDIS_REST_URL")
        self.rest_token = rest_token or os.getenv("UPSTASH_REDIS_REST_TOKEN")
        self.ttl_seconds = ttl_seconds
        self.enabled = bool(self.rest_url and self.rest_token)
        
        if not self.enabled:
            logger.info("Upstash caching disabled (no UPSTASH_REDIS_REST_URL or TOKEN configured)")
        else:
            logger.info(f"Upstash caching enabled with TTL={ttl_seconds}s")
    
    def _make_key(self, vin: str) -> str:
        """Create cache key for a VIN."""
        return f"vin:{vin.upper()}"
    
    async def get(self, vin: str) -> Optional[Dict[str, Any]]:
        """
        Get cached VIN data from Upstash.
        
        Args:
            vin: Vehicle identification number
            
        Returns:
            Cached data if available, None otherwise
        """
        if not self.enabled:
            return None
            
        try:
            key = self._make_key(vin)
            url = f"{self.rest_url}/get/{key}"
            headers = {"Authorization": f"Bearer {self.rest_token}"}
            
            timeout = aiohttp.ClientTimeout(total=5.0)  # 5 second timeout for cache
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("result")
                        if result:
                            logger.info(f"Cache hit for VIN: {vin}")
                            return json.loads(result)
                        else:
                            logger.info(f"Cache miss for VIN: {vin}")
                            return None
                    else:
                        logger.error(f"Upstash GET error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Upstash get error: {e}")
            return None
    
    async def set(self, vin: str, data: Dict[str, Any]) -> bool:
        """
        Cache VIN data to Upstash.
        
        Args:
            vin: Vehicle identification number
            data: Data to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled:
            return False
            
        try:
            key = self._make_key(vin)
            json_data = json.dumps(data)
            url = f"{self.rest_url}/set/{key}/EX/{self.ttl_seconds}"
            headers = {
                "Authorization": f"Bearer {self.rest_token}",
                "Content-Type": "text/plain"
            }
            
            timeout = aiohttp.ClientTimeout(total=5.0)  # 5 second timeout for cache
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, data=json_data) as response:
                    if response.status == 200:
                        logger.info(f"Cached data for VIN: {vin}")
                        return True
                    else:
                        logger.error(f"Upstash SET error: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Upstash set error: {e}")
            return False
    
    async def close(self) -> None:
        """Upstash REST API doesn't need connection management."""
        pass