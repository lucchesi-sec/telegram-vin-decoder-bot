#!/usr/bin/env python3
"""
Debug script to examine Auto.dev API response for multiple VINs
"""

import asyncio
import json
import sys
import os

# Add the project root to the path so we can import vinbot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.autodev_client import AutoDevClient


async def debug_autodev_response():
    # Check if API key is provided
    api_key = os.getenv("AUTODEV_API_KEY")
    if not api_key:
        print("Error: AUTODEV_API_KEY environment variable not set")
        print("Please set it with: export AUTODEV_API_KEY='your-api-key'")
        return
    
    # Create Auto.dev client
    client = AutoDevClient(api_key=api_key)
    
    # List of test VINs (some real ones that should have data)
    test_vins = [
        "1FTEW1E88HKE34785",  # 2017 Ford F-150
        "2T1BURHE5JC023456",  # 2018 Toyota Camry
        "WBAVA33598NL67451",  # 2018 BMW 3 Series
        "JH4NA21691T000123",  # 2001 Acura TL
        "KMHDH4AE8CU456789",  # 2012 Hyundai Elantra
        "1HGBH41JXMN109186"   # 1995 Honda Accord (original test)
    ]
    
    for vin in test_vins:
        print(f"Debugging Auto.dev API response for VIN: {vin}")
        print("=" * 50)
        
        try:
            # Get the raw response from Auto.dev
            url = f"{AutoDevClient.BASE_URL}/vin/{vin.upper()}"
            print(f"Making request to: {url}")
            
            import httpx
            async with httpx.AsyncClient(timeout=15) as httpx_client:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json"
                }
                
                response = await httpx_client.get(url, headers=headers)
                
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    raw_data = response.json()
                    print("\nRaw API Response:")
                    print("-" * 30)
                    print(json.dumps(raw_data, indent=2))
                    
                    # Check if we got actual data or just an error
                    if raw_data.get("status") == "NOT_FOUND":
                        print(f"VIN {vin} not found in Auto.dev database")
                        print()
                        continue
                    
                    # Now test our format_response method
                    print("\nFormatted Response:")
                    print("-" * 30)
                    formatted_data = client.format_response(raw_data)
                    print(json.dumps(formatted_data, indent=2))
                    
                    # Show what we're missing
                    print("\nAvailable top-level keys in raw data:")
                    print("-" * 40)
                    for key in raw_data.keys():
                        print(f"  - {key}")
                        
                    # Check for nested data
                    print("\nDetailed structure analysis:")
                    print("-" * 30)
                    analyze_structure(raw_data, "")
                    
                    # Found a VIN with data, so we can stop
                    print(f"\nSUCCESS: Found data for VIN {vin}")
                    return
                    
                elif response.status_code == 401:
                    print("Error: Invalid API key or unauthorized access")
                    return
                elif response.status_code == 404:
                    print("Error: VIN not found or invalid")
                else:
                    print(f"Error: API returned status {response.status_code}")
                    
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("No VINs with data found in the Auto.dev database with this API key.")


def analyze_structure(data, prefix=""):
    """Recursively analyze the structure of the data"""
    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict, list)) and value:
                if isinstance(value, dict):
                    print(f"  {new_prefix} (dict with {len(value)} keys)")
                    # Show first few keys for large dicts
                    keys = list(value.keys())[:5]
                    if len(value) > 5:
                        print(f"    Keys: {', '.join(keys)} ... ({len(value)} total)")
                    else:
                        print(f"    Keys: {', '.join(keys)}")
                    analyze_structure(value, new_prefix)
                else:  # list
                    print(f"  {new_prefix} (list with {len(value)} items)")
                    if len(value) > 0:
                        item_type = type(value[0]).__name__
                        print(f"    Items are {item_type}")
                        if isinstance(value[0], dict) and len(value) > 0:
                            print(f"    First item keys: {list(value[0].keys())[:5]}")
            else:
                value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"  {new_prefix} = {value_str}")


if __name__ == "__main__":
    asyncio.run(debug_autodev_response())