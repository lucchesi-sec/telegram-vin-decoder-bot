"""Health check utilities."""

import asyncio
from typing import Dict, Any, List
from src.infrastructure.external_services.nhtsa.nhtsa_client import NHTSAClient
from src.infrastructure.external_services.autodev.autodev_client import AutoDevClient


class HealthCheck:
    """Health check utility for monitoring service status."""
    
    def __init__(
        self,
        nhtsa_client: NHTSAClient,
        autodev_client: AutoDevClient
    ):
        self.nhtsa_client = nhtsa_client
        self.autodev_client = autodev_client
    
    async def check_services(self) -> Dict[str, Any]:
        """Check the health of all services.
        
        Returns:
            Dictionary with health status of each service
        """
        results = {}
        
        # Check NHTSA service
        try:
            nhtsa_healthy = await self.nhtsa_client.test_connection()
            results["nhtsa"] = {
                "status": "healthy" if nhtsa_healthy else "unhealthy",
                "details": "NHTSA API is accessible" if nhtsa_healthy else "NHTSA API is not accessible"
            }
        except Exception as e:
            results["nhtsa"] = {
                "status": "unhealthy",
                "details": f"Error checking NHTSA: {str(e)}"
            }
        
        # Check AutoDev service
        try:
            autodev_healthy = await self.autodev_client.test_connection()
            results["autodev"] = {
                "status": "healthy" if autodev_healthy else "unhealthy",
                "details": "AutoDev API is accessible" if autodev_healthy else "AutoDev API is not accessible"
            }
        except Exception as e:
            results["autodev"] = {
                "status": "unhealthy",
                "details": f"Error checking AutoDev: {str(e)}"
            }
        
        # Overall status
        all_healthy = all(service["status"] == "healthy" for service in results.values())
        results["overall"] = {
            "status": "healthy" if all_healthy else "degraded",
            "details": "All services are healthy" if all_healthy else "Some services are unhealthy"
        }
        
        return results
    
    async def get_detailed_health(self) -> Dict[str, Any]:
        """Get detailed health information.
        
        Returns:
            Dictionary with detailed health information
        """
        service_status = await self.check_services()
        
        return {
            "status": service_status["overall"]["status"],
            "timestamp": asyncio.get_event_loop().time(),
            "services": service_status
        }