from __future__ import annotations

import httpx
import logging
import ssl
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


VIN_ENDPOINT = "https://api.carsxe.com/specs"


class CarsXEError(Exception):
    pass


class CarsXEClient:
    def __init__(self, api_key: str, timeout_seconds: int = 15, cache=None):
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None
        self.cache = cache  # Optional cache backend

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            # Create SSL context that's more permissive for production environments
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Configure client with explicit settings to avoid redirect issues
            self._client = httpx.AsyncClient(
                timeout=self.timeout_seconds,
                follow_redirects=False,  # Don't follow redirects automatically
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
                headers={
                    "User-Agent": "VinBot/1.0 (Python/httpx)",
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                verify=ssl_context,
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def decode_vin(self, vin: str) -> Dict[str, Any]:
        # Check cache first if available
        if self.cache:
            cache_key = f"vin:{vin.upper()}"
            try:
                cached_data = await self.cache.get(cache_key)
                if cached_data:
                    logger.info(f"Cache hit for VIN {vin}")
                    import json
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")
        
        client = await self._get_client()
        url = VIN_ENDPOINT
        params = {"key": self.api_key, "vin": vin}
        logger.info(f"Requesting VIN decode from {url} for VIN: {vin}")
        
        try:
            # Log full request details for debugging
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request params: {params}")
            logger.debug(f"Client base headers: {client.headers}")
            
            # Make request with explicit headers (client defaults will be merged)
            resp = await client.get(
                url,
                params=params,
                headers={
                    "Accept": "application/json",
                    "Cache-Control": "no-cache",
                },
            )
            
            # Log response details
            logger.info(f"Response status: {resp.status_code}, Content-Type: {resp.headers.get('content-type', 'unknown')}")
            logger.debug(f"Response headers: {dict(resp.headers)}")
            
            # Check for redirect
            if resp.status_code in (301, 302, 303, 307, 308):
                logger.error(f"Unexpected redirect to: {resp.headers.get('location', 'unknown')}")
                raise CarsXEError(f"API endpoint redirected unexpectedly (status {resp.status_code})")
        except httpx.HTTPError as e:
            logger.error(f"Network error contacting CarsXE: {e}")
            raise CarsXEError(f"Network error contacting CarsXE: {e}") from e

        if resp.status_code >= 400:
            # Check if response is HTML (indicates wrong endpoint or routing issue)
            content_type = resp.headers.get("content-type", "").lower()
            response_preview = resp.text[:500]  # Get more of the response for debugging
            
            logger.error(f"API error - Status: {resp.status_code}, Content-Type: {content_type}")
            logger.error(f"Response preview: {response_preview}")
            
            if "html" in content_type or response_preview.strip().startswith("<"):
                # Try fallback with a fresh client
                logger.warning("HTML response detected, attempting fallback with fresh client")
                return await self._fallback_decode(vin)
            
            raise CarsXEError(
                f"CarsXE responded with {resp.status_code}: {response_preview[:200]}"
            )

        try:
            data = resp.json()
            logger.debug(f"Successfully parsed JSON response with keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict response'}")
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {e}, Response text: {resp.text[:200]}")
            raise CarsXEError(f"Failed to parse CarsXE JSON response: {e}") from e

        # CarsXE may return error in JSON body; try to detect
        if isinstance(data, dict) and data.get("success") is False:
            msg = data.get("message") or data.get("error") or "Unknown CarsXE error"
            logger.error(f"CarsXE API returned error: {msg}")
            raise CarsXEError(str(msg))

        logger.info(f"Successfully decoded VIN {vin}")
        
        # Cache the successful response if cache is available
        if self.cache:
            cache_key = f"vin:{vin.upper()}"
            try:
                import json
                await self.cache.set(cache_key, json.dumps(data))
                logger.debug(f"Cached VIN data for {vin}")
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")
        
        return data
    
    async def _fallback_decode(self, vin: str) -> Dict[str, Any]:
        """Fallback method using a fresh one-shot client"""
        logger.warning(f"Using fallback decode for VIN: {vin}")
        
        # Create a fresh client with minimal configuration
        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
            follow_redirects=True,  # Allow redirects in fallback
        ) as fallback_client:
            url = VIN_ENDPOINT
            params = {"key": self.api_key, "vin": vin}
            
            try:
                resp = await fallback_client.get(
                    url,
                    params=params,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": "Mozilla/5.0 (compatible; VinBot/1.0)",
                    },
                )
                
                if resp.status_code >= 400:
                    raise CarsXEError(f"Fallback also failed with status {resp.status_code}")
                
                data = resp.json()
                
                if isinstance(data, dict) and data.get("success") is False:
                    msg = data.get("message") or data.get("error") or "Unknown CarsXE error"
                    raise CarsXEError(str(msg))
                
                logger.info(f"Fallback decode successful for VIN {vin}")
                return data
                
            except httpx.HTTPError as e:
                logger.error(f"Fallback network error: {e}")
                raise CarsXEError(f"Fallback network error: {e}") from e
            except Exception as e:
                logger.error(f"Fallback decode failed: {e}")
                raise CarsXEError(f"Fallback decode failed: {e}") from e

