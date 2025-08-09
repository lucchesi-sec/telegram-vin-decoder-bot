from __future__ import annotations

import httpx
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


VIN_ENDPOINT = "https://api.carsxe.com/specs"


class CarsXEError(Exception):
    pass


class CarsXEClient:
    def __init__(self, api_key: str, timeout_seconds: int = 15):
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout_seconds)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def decode_vin(self, vin: str) -> Dict[str, Any]:
        client = await self._get_client()
        url = VIN_ENDPOINT
        params = {"key": self.api_key, "vin": vin}
        logger.info(f"Requesting VIN decode from {url} for VIN: {vin}")
        
        try:
            resp = await client.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
            )
            logger.info(f"Response status: {resp.status_code}, Content-Type: {resp.headers.get('content-type', 'unknown')}")
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
                raise CarsXEError(
                    f"CarsXE API returned HTML instead of JSON (status {resp.status_code}). "
                    f"This may indicate a routing or endpoint issue. "
                    f"URL: {url}, Response preview: {response_preview[:200]}"
                )
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
        return data

