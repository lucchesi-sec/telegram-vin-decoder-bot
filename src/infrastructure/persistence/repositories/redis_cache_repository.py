"""Redis cache repository implementation."""

import json
import asyncio
from typing import Optional, Any
from src.domain.vehicle.value_objects import VINNumber


class RedisCacheRepository:
    """Redis implementation of cache repository."""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            # If cache fails, return None
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set a value in cache."""
        try:
            await self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception:
            # If cache fails, silently ignore
            pass
    
    async def delete(self, key: str) -> None:
        """Delete a value from cache."""
        try:
            await self.redis_client.delete(key)
        except Exception:
            # If cache fails, silently ignore
            pass
    
    async def get_vehicle_data(self, vin: VINNumber) -> Optional[dict]:
        """Get vehicle data from cache."""
        cache_key = f"vehicle_data:{vin.value}"
        return await self.get(cache_key)
    
    async def set_vehicle_data(self, vin: VINNumber, data: dict, ttl: int = 3600) -> None:
        """Set vehicle data in cache."""
        cache_key = f"vehicle_data:{vin.value}"
        await self.set(cache_key, data, ttl)