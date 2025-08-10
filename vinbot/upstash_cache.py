from __future__ import annotations

import logging
import os
from typing import Optional

import aiohttp
from urllib.parse import quote

logger = logging.getLogger(__name__)


class UpstashCache:
    """A minimal async key-value cache over Upstash Redis REST API.

    Exposes a generic interface suitable for all callers in this codebase:
      - get(key) -> Optional[str]
      - set(key, value, ttl=None) -> bool
      - delete(key) -> bool
      - aclose() -> None (no-op)
    Callers are responsible for JSON serialization where needed.
    """

    def __init__(self, rest_url: Optional[str] = None, rest_token: Optional[str] = None, ttl_seconds: int = 86400):
        self.rest_url = (rest_url or os.getenv("UPSTASH_REDIS_REST_URL") or "").rstrip("/")
        self.rest_token = rest_token or os.getenv("UPSTASH_REDIS_REST_TOKEN")
        self.default_ttl_seconds = ttl_seconds
        self.enabled = bool(self.rest_url and self.rest_token)

        if not self.enabled:
            logger.info("Upstash caching disabled (no UPSTASH_REDIS_REST_URL or TOKEN configured)")
        else:
            logger.info(f"Upstash caching enabled with default TTL={self.default_ttl_seconds}s")

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.rest_token}"}

    async def get(self, key: str) -> Optional[str]:
        if not self.enabled:
            return None

        try:
            safe_key = quote(key, safe="")
            url = f"{self.rest_url}/get/{safe_key}"
            timeout = aiohttp.ClientTimeout(total=5.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=self._headers()) as response:
                    if response.status != 200:
                        logger.warning(f"Upstash GET error: status={response.status} key={key}")
                        return None
                    payload = await response.json()
                    result = payload.get("result")
                    return result if result is not None else None
        except Exception as e:
            logger.error(f"Upstash GET exception for key='{key}': {e}")
            return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        if not self.enabled:
            return False

        try:
            ttl_to_use = ttl if ttl and ttl > 0 else self.default_ttl_seconds
            safe_key = quote(key, safe="")
            url = f"{self.rest_url}/set/{safe_key}/EX/{ttl_to_use}"
            headers = {**self._headers(), "Content-Type": "text/plain"}
            timeout = aiohttp.ClientTimeout(total=5.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, data=value) as response:
                    if response.status != 200:
                        logger.warning(f"Upstash SET error: status={response.status} key={key}")
                        return False
                    return True
        except Exception as e:
            logger.error(f"Upstash SET exception for key='{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.enabled:
            return False

        try:
            safe_key = quote(key, safe="")
            # Upstash REST: DEL is a POST operation
            url = f"{self.rest_url}/del/{safe_key}"
            timeout = aiohttp.ClientTimeout(total=5.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=self._headers()) as response:
                    if response.status != 200:
                        logger.warning(f"Upstash DEL error: status={response.status} key={key}")
                        return False
                    return True
        except Exception as e:
            logger.error(f"Upstash DEL exception for key='{key}': {e}")
            return False

    async def aclose(self) -> None:
        # Stateless HTTP client; nothing to close
        return None