"""NHTSA adapter implementation."""

from typing import Dict, Any
from src.domain.vehicle.value_objects import VINNumber
from src.infrastructure.external_services.nhtsa.nhtsa_client import NHTSAClient


class NHTSAAdapter:
    """Adapter for NHTSA client to conform to our domain interface."""
    
    def __init__(self, client: NHTSAClient):
        self.client = client
    
    @property
    def service_name(self) -> str:
        """Get the service name."""
        return self.client.service_name
    
    async def decode(self, vin: VINNumber) -> Dict[str, Any]:
        """Decode a VIN using NHTSA service.
        
        Args:
            vin: The VIN to decode
            
        Returns:
            Raw decode result dictionary
        """
        data = await self.client.decode_vin(vin)
        return data