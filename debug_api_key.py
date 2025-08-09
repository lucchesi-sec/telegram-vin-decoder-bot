#!/usr/bin/env python3
"""
Debug script to check if there's an issue with the API key or request parameters
"""
import asyncio
import os
from dotenv import load_dotenv
import httpx
from urllib.parse import urlencode

# Load environment variables
load_dotenv()

VIN_ENDPOINT = "https://api.carsxe.com/specs"

async def test_api_key_directly():
    api_key = os.getenv("CARSXE_API_KEY")
    if not api_key:
        print("CARSXE_API_KEY not found in environment")
        return
    
    print(f"API Key: {api_key}")
    print(f"API Key length: {len(api_key)}")
    
    # Test with the specific VIN that's causing issues
    vin = "WBSJF0C50JB282102"
    print(f"VIN: {vin}")
    
    # Test 1: Direct URL construction
    params = {"key": api_key, "vin": vin}
    url = f"{VIN_ENDPOINT}?{urlencode(params)}"
    print(f"Direct URL: {url}")
    
    # Test 2: Using httpx client like the CarsXE client does
    async with httpx.AsyncClient() as client:
        try:
            print("Making request with httpx client...")
            resp = await client.get(
                VIN_ENDPOINT,
                params=params,
                headers={"Accept": "application/json"},
            )
            print(f"Response status code: {resp.status_code}")
            print(f"Response content type: {resp.headers.get('content-type', 'unknown')}")
            if resp.status_code >= 400:
                print(f"Error response (first 500 chars): {resp.text[:500]}")
            else:
                print("Success! Response received")
                print(f"Response data (first 200 chars): {resp.text[:200]}")
        except Exception as e:
            print(f"Exception during request: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_key_directly())