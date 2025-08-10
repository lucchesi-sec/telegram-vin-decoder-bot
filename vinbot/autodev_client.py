import httpx
import logging
from typing import Dict, Any, Optional
from .vin_decoder_base import VINDecoderBase

logger = logging.getLogger(__name__)


class AutoDevError(Exception):
    """Custom exception for Auto.dev API errors"""
    pass


class AutoDevClient(VINDecoderBase):
    """Auto.dev VIN decoder client"""
    
    BASE_URL = "https://auto.dev/api"
    
    def __init__(self, api_key: str, cache=None, timeout: int = 15):
        """Initialize Auto.dev client
        
        Args:
            api_key: Auto.dev API key
            cache: Optional cache backend
            timeout: Request timeout in seconds
        """
        super().__init__(api_key=api_key, cache=cache, timeout=timeout)
        self.service_name = "AutoDev"
    
    async def decode_vin(self, vin: str) -> Dict[str, Any]:
        """Decode VIN using Auto.dev API
        
        Args:
            vin: Vehicle Identification Number
            
        Returns:
            Dictionary containing vehicle information
            
        Raises:
            AutoDevError: If API request fails
        """
        # Check cache first
        cached = await self.get_cached_result(vin)
        if cached:
            return cached
        
        # Auto.dev API endpoint for VIN decoding
        url = f"{self.BASE_URL}/vin/{vin.upper()}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use Bearer token in header (more secure than query parameter)
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                }
                
                response = await client.get(url, headers=headers)
                
                # Log response status
                logger.info(f"Auto.dev API response status: {response.status_code}")
                
                if response.status_code == 401:
                    raise AutoDevError("Invalid API key or unauthorized access")
                elif response.status_code == 404:
                    raise AutoDevError("VIN not found or invalid")
                elif response.status_code >= 400:
                    raise AutoDevError(f"API error: {response.status_code}")
                
                response.raise_for_status()
                
                data = response.json()
                
                # Format the response to our standard format
                formatted_data = self.format_response(data)
                
                # Cache the result
                await self.cache_result(vin, formatted_data)
                
                return formatted_data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Auto.dev API HTTP error: {e}")
            raise AutoDevError(f"Auto.dev API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Auto.dev API request error: {e}")
            raise AutoDevError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Auto.dev decode: {e}")
            raise AutoDevError(f"Failed to decode VIN: {str(e)}")
    
    def format_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format Auto.dev API response to standardized format
        
        Args:
            data: Raw Auto.dev API response
            
        Returns:
            Standardized dictionary matching our format
        """
        # Extract vehicle information from Auto.dev response
        vehicle_info = {}
        
        # Map Auto.dev fields to our standard format
        # Note: Auto.dev response structure may vary, adjust mappings as needed
        if isinstance(data, dict):
            # Basic vehicle information
            vehicle_info["vin"] = data.get("vin", "")
            vehicle_info["year"] = data.get("year") or data.get("model_year")
            vehicle_info["make"] = data.get("make") or data.get("manufacturer")
            vehicle_info["model"] = data.get("model")
            vehicle_info["trim"] = data.get("trim") or data.get("trim_level")
            vehicle_info["body_type"] = data.get("body_type") or data.get("body_class")
            vehicle_info["vehicle_type"] = data.get("vehicle_type") or data.get("type")
            
            # Engine and drivetrain
            vehicle_info["engine"] = data.get("engine") or data.get("engine_description")
            vehicle_info["cylinders"] = data.get("cylinders") or data.get("engine_cylinders")
            vehicle_info["displacement"] = data.get("displacement") or data.get("engine_displacement")
            vehicle_info["fuel_type"] = data.get("fuel_type") or data.get("fuel")
            vehicle_info["transmission"] = data.get("transmission") or data.get("transmission_type")
            vehicle_info["drive_type"] = data.get("drivetrain") or data.get("drive_type")
            
            # Dimensions and weight
            vehicle_info["doors"] = data.get("doors") or data.get("door_count")
            vehicle_info["seats"] = data.get("seats") or data.get("seating_capacity")
            vehicle_info["weight"] = data.get("curb_weight") or data.get("weight")
            vehicle_info["wheelbase"] = data.get("wheelbase")
            vehicle_info["length"] = data.get("length")
            vehicle_info["width"] = data.get("width")
            vehicle_info["height"] = data.get("height")
            
            # Manufacturing
            vehicle_info["country"] = data.get("country") or data.get("made_in")
            vehicle_info["manufacturer"] = data.get("manufacturer") or data.get("make")
            vehicle_info["plant"] = data.get("plant") or data.get("factory")
            
            # Additional data
            vehicle_info["msrp"] = data.get("msrp") or data.get("base_price")
            vehicle_info["mpg_city"] = data.get("mpg_city") or data.get("city_mpg")
            vehicle_info["mpg_highway"] = data.get("mpg_highway") or data.get("highway_mpg")
            
            # Features and options (if available)
            if "features" in data:
                vehicle_info["features"] = data["features"]
            if "standard_equipment" in data:
                vehicle_info["standard_equipment"] = data["standard_equipment"]
            if "optional_equipment" in data:
                vehicle_info["optional_equipment"] = data["optional_equipment"]
            
            # Market data (if available)
            if "market_value" in data or "pricing" in data:
                vehicle_info["market_value"] = data.get("market_value") or data.get("pricing")
            
            # History (if available)
            if "history" in data or "recalls" in data:
                vehicle_info["history"] = data.get("history")
                vehicle_info["recalls"] = data.get("recalls")
        
        # Remove None values
        vehicle_info = {k: v for k, v in vehicle_info.items() if v is not None}
        
        # Format in a structure similar to CarsXE for compatibility
        formatted = {
            "success": True,
            "vin": data.get("vin", ""),
            "attributes": vehicle_info,
            "service": "AutoDev",
            "cached": False,
            "raw_data": data  # Keep raw data for reference
        }
        
        # Include additional data sections if available
        if "pricing" in data:
            formatted["marketvalue"] = data["pricing"]
        if "history" in data:
            formatted["history"] = data["history"]
        if "recalls" in data:
            formatted["recalls"] = data["recalls"]
        
        return formatted
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate if the API key format is correct
        
        Auto.dev API keys are base64 encoded strings
        """
        if not api_key:
            return False
        
        # Basic validation - Auto.dev keys are typically base64 encoded
        # and end with == or =
        import re
        pattern = r'^[A-Za-z0-9+/]+=*$'
        return bool(re.match(pattern, api_key)) and len(api_key) >= 20
    
    async def test_connection(self) -> bool:
        """Test if Auto.dev API is accessible with the provided key
        
        Returns:
            True if API is accessible and key is valid, False otherwise
        """
        try:
            # Test with a known VIN
            test_vin = "ZPBUA1ZL9KLA00848"
            url = f"{self.BASE_URL}/vin/{test_vin}"
            
            async with httpx.AsyncClient(timeout=5) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                }
                response = await client.get(url, headers=headers)
                
                # 200 means success, 401 means invalid key, 404 means VIN not found (but API works)
                return response.status_code in [200, 404]
        except:
            return False