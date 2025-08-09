from __future__ import annotations

import httpx
from typing import Any, Dict, Optional

from .redis_cache import RedisCache


VIN_ENDPOINT = "https://api.carsxe.com/specs"


class CarsXEError(Exception):
    pass


class CarsXEClient:
    def __init__(self, api_key: str, timeout_seconds: int = 15, cache: Optional[RedisCache] = None):
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None
        self.cache = cache or RedisCache()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout_seconds)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        if self.cache:
            await self.cache.close()

    async def decode_vin(self, vin: str) -> Dict[str, Any]:
        # Check cache first with error handling
        if self.cache:
            try:
                cached_data = await self.cache.get(vin)
                if cached_data and isinstance(cached_data, dict):
                    # Validate cached data - ensure it's not an error response
                    if cached_data.get("success") is not False:
                        return cached_data
                    # If cached data indicates failure, ignore it and fetch fresh
            except Exception as cache_error:
                # Log cache error but continue to API call
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Cache get error for VIN {vin}: {cache_error}")
        
        client = await self._get_client()
        try:
            resp = await client.get(
                VIN_ENDPOINT,
                params={"key": self.api_key, "vin": vin},
                headers={"Accept": "application/json"},
            )
        except httpx.HTTPError as e:
            raise CarsXEError(f"Network error contacting CarsXE: {e}") from e

        if resp.status_code >= 400:
            # Check if response is HTML (indicates wrong endpoint or routing issue)
            content_type = resp.headers.get("content-type", "").lower()
            if "html" in content_type:
                raise CarsXEError(
                    f"CarsXE API returned HTML instead of JSON (status {resp.status_code}). "
                    "This may indicate a routing or endpoint configuration issue."
                )
            raise CarsXEError(
                f"CarsXE responded with {resp.status_code}: {resp.text[:200]}"
            )

        try:
            data = resp.json()
        except Exception as e:
            raise CarsXEError(f"Failed to parse CarsXE JSON response: {e}") from e

        # CarsXE may return error in JSON body; try to detect
        if isinstance(data, dict) and data.get("success") is False:
            msg = data.get("message") or data.get("error") or "Unknown CarsXE error"
            raise CarsXEError(str(msg))

        # Cache successful response with error handling
        if self.cache:
            try:
                await self.cache.set(vin, data)
            except Exception as cache_error:
                # Log cache error but don't fail the request
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Cache set error for VIN {vin}: {cache_error}")

        return data

