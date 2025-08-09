from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class VINDecoderBase(ABC):
    """Abstract base class for VIN decoder services"""
    
    def __init__(self, api_key: Optional[str] = None, cache=None, timeout: int = 15):
        """Initialize the decoder with optional API key and cache"""
        self.api_key = api_key
        self.cache = cache
        self.timeout = timeout
        self.service_name = self.__class__.__name__.replace("Client", "")
    
    @abstractmethod
    async def decode_vin(self, vin: str) -> Dict[str, Any]:
        """Decode a VIN and return vehicle information
        
        Args:
            vin: Vehicle Identification Number
            
        Returns:
            Dictionary containing vehicle information
            
        Raises:
            Exception: If decoding fails
        """
        pass
    
    @abstractmethod
    def format_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the raw API response into a standardized format
        
        Args:
            data: Raw API response
            
        Returns:
            Standardized dictionary with vehicle information
        """
        pass
    
    @abstractmethod
    def validate_api_key(self, api_key: str) -> bool:
        """Validate if the API key format is correct
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if the API key appears valid, False otherwise
        """
        pass
    
    async def get_cached_result(self, vin: str) -> Optional[Dict[str, Any]]:
        """Get cached result for a VIN if available"""
        if not self.cache:
            return None
            
        try:
            cache_key = f"vin:{self.service_name.lower()}:{vin.upper()}"
            result = await self.cache.get(cache_key)
            if result:
                logger.info(f"Cache hit for VIN {vin} from {self.service_name}")
                return result
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    async def cache_result(self, vin: str, data: Dict[str, Any], ttl: int = 86400) -> None:
        """Cache the result for a VIN"""
        if not self.cache:
            return
            
        try:
            cache_key = f"vin:{self.service_name.lower()}:{vin.upper()}"
            await self.cache.set(cache_key, data, ttl=ttl)
            logger.info(f"Cached result for VIN {vin} from {self.service_name}")
        except Exception as e:
            logger.error(f"Cache set error: {e}")