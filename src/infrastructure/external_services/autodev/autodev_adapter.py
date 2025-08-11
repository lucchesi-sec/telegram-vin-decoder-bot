"""AutoDev adapter implementation."""

from typing import Dict, Any
from src.domain.vehicle.value_objects import VINNumber
from src.infrastructure.external_services.autodev.autodev_client import AutoDevClient


class AutoDevAdapter:
    """Adapter for AutoDev client to conform to our domain interface."""
    
    def __init__(self, client: AutoDevClient):
        self.client = client
    
    @property
    def service_name(self) -> str:
        """Get the service name."""
        return self.client.service_name
    
    async def decode(self, vin: VINNumber) -> Dict[str, Any]:
        """Decode a VIN using AutoDev service.
        
        Args:
            vin: The VIN to decode
            
        Returns:
            Raw decode result dictionary
        """
        data = await self.client.decode_vin(vin)
        return data