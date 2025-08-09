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

# Current endpoint we're using
CARSXE_ENDPOINT = "https://api.carsxe.com/specs"

# Additional endpoints to test (if available)
# Let's try to find if there are other endpoints that might provide more details
ENDPOINTS = {
    "current_carsxe": f"{CARSXE_ENDPOINT}?key={CARSXE_API_KEY}&vin={TEST_VIN}",
    # Let's try with different parameters to see if we can get more details
    "carsxe_detailed": f"{CARSXE_ENDPOINT}?key={CARSXE_API_KEY}&vin={TEST_VIN}&format=json&include=full",
    "carsxe_with_colors": f"{CARSXE_ENDPOINT}?key={CARSXE_API_KEY}&vin={TEST_VIN}&with_colors=true",
    "carsxe_with_equipment": f"{CARSXE_ENDPOINT}?key={CARSXE_API_KEY}&vin={TEST_VIN}&with_equipment=true",
}

async def fetch_vin_data(client: httpx.AsyncClient, name: str, url: str) -> Dict[str, Any]:
    """Fetch VIN data from an endpoint and return the response"""
    print(f"Fetching data from {name}...")
    try:
        response = await client.get(url)
        print(f"{name} status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return {"name": name, "data": data, "status": "success"}
        else:
            print(f"{name} error: {response.status_code}")
            return {"name": name, "data": None, "status": "error", "code": response.status_code}
    except Exception as e:
        print(f"{name} exception: {e}")
        return {"name": name, "data": None, "status": "exception", "error": str(e)}

def count_nested_keys(data: Any, prefix: str = "") -> Dict[str, int]:
    """Recursively count keys in nested dictionaries"""
    counts = {}
    if isinstance(data, dict):
        counts[prefix or "root"] = len(data)
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict, list)):
                nested_counts = count_nested_keys(value, new_prefix)
                counts.update(nested_counts)
            else:
                counts[new_prefix] = 1
    elif isinstance(data, list):
        counts[prefix or "root"] = len(data)
        for i, item in enumerate(data):
            new_prefix = f"{prefix}[{i}]" if prefix else f"[{i}]"
            if isinstance(item, (dict, list)):
                nested_counts = count_nested_keys(item, new_prefix)
                counts.update(nested_counts)
            else:
                counts[new_prefix] = 1
    return counts

def analyze_data_structure(data: Dict[str, Any]) -> None:
    """Analyze the structure of the data and print key statistics"""
    if not isinstance(data, dict):
        print("  - Response is not a dictionary")
        return
    
    # Count keys at different levels
    key_counts = count_nested_keys(data)
    
    # Find the deepest nested keys
    max_depth = max(len(key.split('.')) for key in key_counts.keys())
    
    # Count total keys
    total_keys = len(key_counts)
    
    # Find largest sections
    section_sizes = {}
    for key, count in key_counts.items():
        parts = key.split('.')
        if len(parts) > 1:
            section = parts[0]
            section_sizes[section] = section_sizes.get(section, 0) + 1
    
    print(f"  - Total nested keys: {total_keys}")
    print(f"  - Maximum depth: {max_depth}")
    
    # Show section sizes
    print("  - Section sizes:")
    for section, size in sorted(section_sizes.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    {section}: {size} keys")
    
    # Show some sample data from key sections
    print("  - Sample data from key sections:")
    for section in ['attributes', 'equipment', 'colors', 'warranties']:
        if section in data and data[section]:
            if isinstance(data[section], dict):
                print(f"    {section}: {len(data[section])} items")
                # Show first few items
                items = list(data[section].items()) if isinstance(data[section], dict) else list(enumerate(data[section]))
                for key, value in items[:3]:
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"      {key}: {value}")
            elif isinstance(data[section], list):
                print(f"    {section}: {len(data[section])} items")
                for i, item in enumerate(data[section][:3]):
                    if isinstance(item, dict):
                        print(f"      [{i}]: {len(item)} keys")
                    else:
                        print(f"      [{i}]: {item}")

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
                analyze_data_structure(result["data"])
            else:
                print(f"  - Status: {result['status']}")

if __name__ == "__main__":
    asyncio.run(main())