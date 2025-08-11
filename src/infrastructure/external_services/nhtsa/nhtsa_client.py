"""NHTSA client implementation."""

import httpx
import logging
from typing import Dict, Any, Optional
from src.domain.vehicle.value_objects import VINNumber

logger = logging.getLogger(__name__)


class NHTSAClient:
    """NHTSA VIN decoder client (free, no API key required)."""
    
    BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"
    
    def __init__(self, timeout: int = 15):
        """Initialize NHTSA client."""
        self.timeout = timeout
        self.service_name = "NHTSA"
    
    async def decode_vin(self, vin: VINNumber) -> Dict[str, Any]:
        """Decode VIN using NHTSA API.
        
        Args:
            vin: Vehicle Identification Number
            
        Returns:
            Dictionary containing vehicle information
            
        Raises:
            Exception: If API request fails
        """
        # NHTSA API endpoint
        url = f"{self.BASE_URL}/DecodeVin/{vin.value}?format=json"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                data = response.json()
                
                # Check if the response has results
                if not data.get("Results"):
                    raise Exception("No results returned from NHTSA API")
                
                # Format the response to our standard format
                formatted_data = self.format_response(data)
                
                return formatted_data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"NHTSA API HTTP error: {e}")
            raise Exception(f"NHTSA API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"NHTSA API request error: {e}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in NHTSA decode: {e}")
            raise Exception(f"Failed to decode VIN: {str(e)}")
    
    def format_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format NHTSA API response to standardized format.
        
        Args:
            data: Raw NHTSA API response
            
        Returns:
            Standardized dictionary for downstream formatters
        """
        results = data.get("Results", [])
        
        # Extract relevant fields from NHTSA response
        vehicle_info = {}
        for item in results:
            variable = item.get("Variable", "")
            value = item.get("Value")
            
            if value and value != "Not Applicable":
                # Map NHTSA fields to our standard format
                if variable == "Make":
                    vehicle_info["make"] = value
                elif variable == "Model":
                    vehicle_info["model"] = value
                elif variable == "Model Year":
                    vehicle_info["year"] = value
                elif variable == "Body Class":
                    vehicle_info["body_type"] = value
                elif variable == "Vehicle Type":
                    vehicle_info["vehicle_type"] = value
                elif variable == "Plant City":
                    vehicle_info["plant_city"] = value
                elif variable == "Plant Country":
                    vehicle_info["plant_country"] = value
                elif variable == "Plant State":
                    vehicle_info["plant_state"] = value
                elif variable == "Manufacturer Name":
                    vehicle_info["manufacturer"] = value
                elif variable == "Engine Number of Cylinders":
                    vehicle_info["cylinders"] = value
                elif variable == "Displacement (L)":
                    vehicle_info["displacement_l"] = value
                elif variable == "Fuel Type - Primary":
                    vehicle_info["fuel_type"] = value
                elif variable == "Drive Type":
                    vehicle_info["drive_type"] = value
                elif variable == "Transmission Style":
                    vehicle_info["transmission"] = value
                elif variable == "Number of Doors":
                    vehicle_info["doors"] = value
                elif variable == "Gross Vehicle Weight Rating From":
                    vehicle_info["gvwr"] = value
                elif variable == "Trim":
                    vehicle_info["trim"] = value
                elif variable == "Series":
                    vehicle_info["series"] = value
        
        # Standardized structure for downstream formatters
        formatted = {
            "success": True,
            "vin": data.get("SearchCriteria", "").replace("VIN:", ""),
            "attributes": vehicle_info,
            "service": "NHTSA",
            "raw_data": results  # Keep raw data for reference
        }
        
        return formatted
    
    async def test_connection(self) -> bool:
        """Test if NHTSA API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Test with a known good VIN
            test_vin = "1HGBH41JXMN109186"
            url = f"{self.BASE_URL}/DecodeVin/{test_vin}?format=json"
            
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                return response.status_code == 200
        except:
            return False