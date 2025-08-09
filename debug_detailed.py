#!/usr/bin/env python3
"""
Debug script to add detailed logging to the CarsXE client
"""
import asyncio
import os
from dotenv import load_dotenv
import httpx
from typing import Any, Dict, Optional

# Load environment variables
load_dotenv()

VIN_ENDPOINT = "https://api.carsxe.com/specs"

class DebugCarsXEClient:
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
        
        # Print the exact URL being constructed
        url = f"{VIN_ENDPOINT}?key={self.api_key}&vin={vin}"
        print(f"Making request to: {url}")
        
        try:
            resp = await client.get(
                VIN_ENDPOINT,
                params={"key": self.api_key, "vin": vin},
                headers={"Accept": "application/json"},
            )
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            raise Exception(f"Network error contacting CarsXE: {e}") from e

        print(f"Response status code: {resp.status_code}")
        print(f"Response headers: {dict(resp.headers)}")
        print(f"Response content type: {resp.headers.get('content-type', 'unknown')}")
        print(f"Response text (first 500 chars): {resp.text[:500]}")
        
        if resp.status_code >= 400:
            raise Exception(
                f"CarsXE responded with {resp.status_code}: {resp.text[:200]}"
            )

        try:
            data = resp.json()
        except Exception as e:
            raise Exception("Failed to parse CarsXE JSON response") from e

        # CarsXE may return error in JSON body; try to detect
        if isinstance(data, dict) and data.get("success") is False:
            msg = data.get("message") or data.get("error") or "Unknown CarsXE error"
            raise Exception(str(msg))

        return data

async def test_with_debug():
    api_key = os.getenv("CARSXE_API_KEY")
    if not api_key:
        print("CARSXE_API_KEY not found in environment")
        return
    
    print(f"API Key: {api_key}")
    
    # Test with the specific VIN that's causing issues
    vin = "WBSJF0C50JB282102"
    print(f"VIN: {vin}")
    
    client = DebugCarsXEClient(api_key=api_key)
    
    try:
        print(f"Attempting to decode VIN: {vin}")
        data = await client.decode_vin(vin)
        print("Success! Response data:")
        print(f"Make: {data.get('attributes', {}).get('make', 'N/A')}")
        print(f"Model: {data.get('attributes', {}).get('model', 'N/A')}")
        print(f"Year: {data.get('attributes', {}).get('year', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_with_debug())