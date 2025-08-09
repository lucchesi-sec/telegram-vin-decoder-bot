#!/usr/bin/env python3

import asyncio
import httpx
import json
import os
from typing import Dict, Any

# Get API key from environment
CARSXE_API_KEY = os.environ.get("CARSXE_API_KEY")
if not CARSXE_API_KEY:
    raise ValueError("Please set CARSXE_API_KEY environment variable")

# Test VIN
TEST_VIN = "WDD2J6BB2KA047394"

# Different endpoints to test
ENDPOINTS = {
    "specs_endpoint": f"https://api.carsxe.com/specs?key={CARSXE_API_KEY}&vin={TEST_VIN}",
    "vin_endpoint": f"https://api.carsxe.com/vin?key={CARSXE_API_KEY}&vin={TEST_VIN}",
}

async def fetch_vin_data(client: httpx.AsyncClient, name: str, url: str) -> Dict[str, Any]:
    """Fetch VIN data from an endpoint and return the response"""
    print(f"Fetching data from {name}...")
    print(f"URL: {url}")
    try:
        response = await client.get(url)
        print(f"{name} status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return {"name": name, "data": data, "status": "success"}
        else:
            print(f"{name} error: {response.status_code} - {response.text[:200]}")
            return {"name": name, "data": None, "status": "error", "code": response.status_code}
    except Exception as e:
        print(f"{name} exception: {e}")
        return {"name": name, "data": None, "status": "exception", "error": str(e)}

def count_data_details(data: Dict[str, Any]) -> None:
    """Count and display details about the data structure"""
    if not isinstance(data, dict):
        print("  - Response is not a dictionary")
        return
    
    # Count top-level keys
    print(f"  - Top-level keys: {len(data)}")
    
    # Count attributes if present
    if "attributes" in data and isinstance(data["attributes"], dict):
        print(f"  - Attributes: {len(data['attributes'])}")
        
        # Show some sample attributes
        attrs = data["attributes"]
        print("  - Sample attributes:")
        for key in list(attrs.keys())[:10]:  # Show first 10 keys
            value = attrs[key]
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f"    {key}: {value}")
    
    # Count other sections
    for section in ["equipment", "colors", "warranties"]:
        if section in data:
            if isinstance(data[section], list):
                print(f"  - {section}: {len(data[section])} items")
            elif isinstance(data[section], dict):
                print(f"  - {section}: {len(data[section])} keys")

async def main():
    """Test different VIN decoding endpoints"""
    print(f"Testing VIN: {TEST_VIN}")
    
    # Create HTTP client
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fetch data from all endpoints
        results = []
        for name, url in ENDPOINTS.items():
            result = await fetch_vin_data(client, name, url)
            results.append(result)
        
        # Compare results
        print("\n" + "="*50)
        print("COMPARISON RESULTS")
        print("="*50)
        
        for result in results:
            print(f"\n{result['name']}:")
            if result["status"] == "success":
                count_data_details(result["data"])
            else:
                print(f"  - Status: {result['status']}")

if __name__ == "__main__":
    asyncio.run(main())