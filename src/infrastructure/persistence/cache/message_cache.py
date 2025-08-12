"""Message caching for formatted vehicle data."""

import hashlib
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MessageCache:
    """Cache for formatted Telegram messages to avoid re-processing."""

    def __init__(self, cache_backend):
        """Initialize message cache.

        Args:
            cache_backend: Cache backend (e.g., UpstashCache)
        """
        self.cache = cache_backend
        self.default_ttl = 3600  # 1 hour default

    @staticmethod
    def _generate_key(data: Dict[str, Any], format_type: str) -> str:
        """Generate cache key from data and format type.

        Args:
            data: Vehicle data dictionary
            format_type: Type of formatting (e.g., 'summary', 'features', 'category')

        Returns:
            Cache key string
        """
        # Create a stable hash from the data
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]
        return f"msg:{format_type}:{data_hash}"

    async def get_formatted_message(self, data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Get cached formatted message.

        Args:
            data: Vehicle data dictionary
            format_type: Type of formatting

        Returns:
            Cached formatted message or None
        """
        if not self.cache:
            return None

        try:
            key = self._generate_key(data, format_type)
            cached = await self.cache.get(key)

            if cached and isinstance(cached, dict):
                logger.debug(f"Message cache hit for {format_type}")
                return cached.get("message")

            logger.debug(f"Message cache miss for {format_type}")
            return None
        except Exception as e:
            logger.error(f"Error getting cached message: {e}")
            return None

    async def set_formatted_message(
        self, data: Dict[str, Any], format_type: str, message: str, ttl: Optional[int] = None
    ) -> bool:
        """Cache formatted message.

        Args:
            data: Vehicle data dictionary
            format_type: Type of formatting
            message: Formatted message to cache
            ttl: Time to live in seconds

        Returns:
            True if cached successfully
        """
        if not self.cache:
            return False

        try:
            key = self._generate_key(data, format_type)
            ttl = ttl or self.default_ttl

            cache_data = {
                "message": message,
                "format_type": format_type,
                "cached_at": json.dumps({"timestamp": "now"}),
            }

            result = await self.cache.set(key, cache_data, ttl)
            if result:
                logger.debug(f"Cached message for {format_type}")
            return result
        except Exception as e:
            logger.error(f"Error caching message: {e}")
            return False

    async def invalidate_vehicle_messages(self, vin: str) -> int:
        """Invalidate all cached messages for a vehicle.

        Args:
            vin: Vehicle identification number

        Returns:
            Number of keys invalidated
        """
        if not self.cache:
            return 0

        # Note: This is a simplified implementation
        # In production, you might want to track keys per VIN
        logger.info(f"Invalidating cached messages for VIN: {vin}")
        return 0


class CachedVehicleFormatter:
    """Vehicle formatter with caching support."""

    def __init__(self, message_cache: MessageCache):
        """Initialize cached formatter.

        Args:
            message_cache: Message cache instance
        """
        self.cache = message_cache

    async def format_summary_cached(self, vehicle_data: Dict[str, Any], formatter_func) -> str:
        """Format vehicle summary with caching.

        Args:
            vehicle_data: Vehicle data dictionary
            formatter_func: Function to format data if not cached

        Returns:
            Formatted message
        """
        # Try to get from cache
        cached = await self.cache.get_formatted_message(vehicle_data, "summary")
        if cached:
            return cached

        # Format and cache
        formatted = formatter_func(vehicle_data)
        await self.cache.set_formatted_message(vehicle_data, "summary", formatted)

        return formatted

    async def format_features_cached(
        self, vehicle_data: Dict[str, Any], formatter_func, page: int = 1
    ) -> str:
        """Format features with caching.

        Args:
            vehicle_data: Vehicle data dictionary
            formatter_func: Function to format data if not cached
            page: Page number for pagination

        Returns:
            Formatted message
        """
        # Create a key that includes page number
        cache_data = {**vehicle_data, "page": page}

        # Try to get from cache
        cached = await self.cache.get_formatted_message(cache_data, f"features_p{page}")
        if cached:
            return cached

        # Format and cache
        formatted = formatter_func(vehicle_data)
        await self.cache.set_formatted_message(
            cache_data, f"features_p{page}", formatted, ttl=1800  # 30 min for paginated content
        )

        return formatted
