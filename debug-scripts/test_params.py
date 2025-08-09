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

# Base endpoint
BASE_ENDPOINT = "https://api.carsxe.com/specs"

# Different parameter combinations to test
PARAM_COMBINATIONS = {
    "default": {"key": CARSXE_API_KEY, "vin": TEST_VIN},
    "with_format": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "format": "json"},
    "with_detailed": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "detailed": "true"},
    "with_full": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "full": "true"},
    "with_extended": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "extended": "true"},
    "with_all": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "all": "true"},
    "with_equipment": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "with_equipment": "true"},
    "with_colors": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "with_colors": "true"},
    "with_warranties": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "with_warranties": "true"},
    "with_images": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "with_images": "true"},
    "with_specs": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "with_specs": "true"},
    "with_details": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "with_details": "true"},
    "level_max": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "level": "max"},
    "level_detailed": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "level": "detailed"},
    "level_full": {"key": CARSXE_API_KEY, "vin": TEST_VIN, "level": "full"},
}

async def fetch_vin_data(client: httpx.AsyncClient, name: str, params: Dict[str, str]) -> Dict[str, Any]:
    """Fetch VIN data from an endpoint with specific parameters"""
    print(f"Testing parameter combination: {name}")
    try:
        response = await client.get(BASE_ENDPOINT, params=params)
        print(f"  Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Count the total number of keys in the response
            def count_keys(obj):
                if isinstance(obj, dict):
                    count = len(obj)
                    for value in obj.values():
                        count += count_keys(value)
                    return count
                elif isinstance(obj, list):
                    count = len(obj)
                    for item in obj:
                        count += count_keys(item)
                    return count
                else:
                    return 1
            
            total_keys = count_keys(data)
            return {"name": name, "data": data, "status": "success", "total_keys": total_keys}
        else:
            return {"name": name, "data": None, "status": "error", "code": response.status_code}
    except Exception as e:
        print(f"  Exception: {e}")
        return {"name": name, "data": None, "status": "exception", "error": str(e)}

async def main():
    """Test different parameter combinations with the CarsXE API"""
    print(f"Testing VIN: {TEST_VIN}")
    print(f"Base endpoint: {BASE_ENDPOINT}")
    
    # Create HTTP client
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fetch data with all parameter combinations
        results = []
        for name, params in PARAM_COMBINATIONS.items():
            result = await fetch_vin_data(client, name, params)
            results.append(result)
        
        # Compare results
        print("\n" + "="*60)
        print("COMPARISON RESULTS (sorted by total keys count)")
        print("="*60)
        
        # Sort results by total keys count (descending)
        sorted_results = sorted(
            [r for r in results if r["status"] == "success"], 
            key=lambda x: x["total_keys"], 
            reverse=True
        )
        
        # Display results
        for result in sorted_results:
            print(f"\n{result['name']}:")
            print(f"  Total keys in response: {result['total_keys']}")
            
            # Show some details about the data structure
            data = result["data"]
            if isinstance(data, dict):
                print(f"  Top-level sections: {len(data)}")
                for key in data.keys():
                    if isinstance(data[key], dict):
                        print(f"    {key}: {len(data[key])} items")
                    elif isinstance(data[key], list):
                        print(f"    {key}: {len(data[key])} items")
        
        # Show any failed requests
        failed_results = [r for r in results if r["status"] != "success"]
        if failed_results:
            print("\n" + "="*60)
            print("FAILED REQUESTS")
            print("="*60)
            
            for result in failed_results:
                print(f"\n{result['name']}: {result['status']}")
                if result["status"] == "error":
                    print(f"  Status code: {result['code']}")

if __name__ == "__main__":
    asyncio.run(main())