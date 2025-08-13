"""Shared API client for internal communication between presentation layers."""

import httpx
import asyncio
from typing import Optional, Dict, Any, List
from src.presentation.shared.dto.vehicle_dto import VehicleResponseDTO, VehicleDecodeResponseDTO
from src.presentation.shared.dto.user_dto import UserResponseDTO


class InternalAPIClient:
    """Client for internal API communication following DDD principles."""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._token: Optional[str] = None
    
    def set_auth_token(self, token: str) -> None:
        """Set the JWT token for authenticated requests."""
        self._token = token
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers
    
    async def authenticate_telegram_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Authenticate a Telegram user and get JWT token."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/auth/telegram",
                json={
                    "telegram_id": telegram_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name
                },
                headers=self._get_headers()
            )
            response.raise_for_status()
            auth_data = response.json()
            
            # Store the token for future requests
            self.set_auth_token(auth_data["access_token"])
            return auth_data
    
    async def decode_vin(self, vin: str) -> VehicleDecodeResponseDTO:
        """Decode a VIN through the API."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/vehicles/decode",
                json={"vin": vin},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return VehicleDecodeResponseDTO(**response.json())
    
    async def get_user_vehicles(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get user's vehicle history."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/vehicles",
                params={"page": page, "limit": limit},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
        """Delete a vehicle."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}/api/vehicles/{vehicle_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_current_user(self) -> UserResponseDTO:
        """Get current user information."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/users/me",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return UserResponseDTO(**response.json())
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get application statistics."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/stats",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()