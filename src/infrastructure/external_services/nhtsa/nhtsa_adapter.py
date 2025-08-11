"""NHTSA adapter implementation."""

from src.domain.vehicle.value_objects import VINNumber, DecodeResult
from src.infrastructure.external_services.nhtsa.nhtsa_client import NHTSAClient


class NHTSAAdapter:
    """Adapter for NHTSA client to conform to our domain interface."""
    
    def __init__(self, client: NHTSAClient):
        self.client = client
    
    async def decode(self, vin: VINNumber) -> DecodeResult:
        """Decode a VIN using NHTSA service.
        
        Args:
            vin: The VIN to decode
            
        Returns:
            Decode result
        """
        try:
            data = await self.client.decode_vin(vin)
            return DecodeResult(
                vin=vin,
                success=True,
                data=data,
                service_used=self.client.service_name
            )
        except Exception as e:
            return DecodeResult(
                vin=vin,
                success=False,
                data={},
                service_used=self.client.service_name,
                error_message=str(e)
            )