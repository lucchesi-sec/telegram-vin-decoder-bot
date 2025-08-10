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
                
        # Format the response to our standardized format
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
            if isinstance(data.get("make"), dict):
                vehicle_info["make"] = data["make"].get("name", "")
            else:
                vehicle_info["make"] = data.get("make", "")
                
            if isinstance(data.get("model"), dict):
                vehicle_info["model"] = data["model"].get("name", "")
            else:
                vehicle_info["model"] = data.get("model", "")
                
            vehicle_info["year"] = None
            if "years" in data and isinstance(data["years"], list) and len(data["years"]) > 0:
                vehicle_info["year"] = data["years"][0].get("year")
            
            # Engine information
            if "engine" in data and isinstance(data["engine"], dict):
                engine = data["engine"]
                vehicle_info["engine"] = engine.get("name", "")
                vehicle_info["cylinders"] = engine.get("cylinder")
                vehicle_info["displacement"] = engine.get("size")
                vehicle_info["fuel_type"] = engine.get("fuelType")
                vehicle_info["horsepower"] = engine.get("horsepower")
                vehicle_info["torque"] = engine.get("torque")
                vehicle_info["configuration"] = engine.get("configuration")
                vehicle_info["compressor_type"] = engine.get("compressorType")
            
            # Transmission information
            if "transmission" in data and isinstance(data["transmission"], dict):
                transmission = data["transmission"]
                vehicle_info["transmission"] = transmission.get("name", "")
                vehicle_info["transmission_type"] = transmission.get("transmissionType")
                vehicle_info["number_of_speeds"] = transmission.get("numberOfSpeeds")
                vehicle_info["automatic_type"] = transmission.get("automaticType")
            
            # Body and drive information
            vehicle_info["drive_type"] = data.get("drivenWheels")
            vehicle_info["doors"] = data.get("numOfDoors")
            
            if "categories" in data and isinstance(data["categories"], dict):
                categories = data["categories"]
                vehicle_info["body_type"] = categories.get("primaryBodyType")
                vehicle_info["vehicle_style"] = categories.get("vehicleStyle")
                vehicle_info["vehicle_size"] = categories.get("vehicleSize")
                vehicle_info["epa_class"] = categories.get("epaClass")
            
            # Fuel economy
            if "mpg" in data and isinstance(data["mpg"], dict):
                mpg = data["mpg"]
                vehicle_info["mpg_city"] = mpg.get("city")
                vehicle_info["mpg_highway"] = mpg.get("highway")
            
            # Trim information
            if "years" in data and isinstance(data["years"], list) and len(data["years"]) > 0:
                year_info = data["years"][0]
                if "styles" in year_info and isinstance(year_info["styles"], list) and len(year_info["styles"]) > 0:
                    style = year_info["styles"][0]
                    vehicle_info["trim"] = style.get("trim")
            
            # Extract options as features
            if "options" in data and isinstance(data["options"], list):
                features = []
                for category in data["options"]:
                    if isinstance(category, dict) and "options" in category:
                        for option in category["options"]:
                            if isinstance(option, dict) and "name" in option:
                                features.append(option["name"])
                if features:
                    vehicle_info["features"] = features
            
            # Extract colors
            if "colors" in data and isinstance(data["colors"], list):
                colors = []
                for category in data["colors"]:
                    if isinstance(category, dict) and "options" in category:
                        for color in category["options"]:
                            if isinstance(color, dict) and "name" in color:
                                colors.append(color["name"])
                if colors:
                    vehicle_info["colors"] = colors
        
        # Remove None values
        vehicle_info = {k: v for k, v in vehicle_info.items() if v is not None}
        
        # Standardized structure for downstream formatters
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