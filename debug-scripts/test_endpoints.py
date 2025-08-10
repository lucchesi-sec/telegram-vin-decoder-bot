#!/usr/bin/env python3
"""
Test different CarsXE API endpoints to compare detail levels
"""

import asyncio
import json
import os
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("CARSXE_API_KEY")
if not API_KEY:
    print("Error: CARSXE_API_KEY not found in environment")
    exit(1)

TEST_VIN = "WDD2J6BB2KA047394"

async def test_endpoint(endpoint: str, vin: str) -> Dict[str, Any]:
    """Test a specific CarsXE API endpoint"""
    url = f"https://api.carsxe.com/{endpoint}"
    params = {
        "key": API_KEY,
        "vin": vin
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def count_fields(data: Dict[str, Any], prefix: str = "") -> int:
    """Count non-null fields in the response"""
    count = 0
    for key, value in data.items():
        if value is not None and value != "" and value != []:
            if isinstance(value, dict):
                count += count_fields(value, f"{prefix}{key}.")
            else:
                count += 1
    return count

def extract_key_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key information from response"""
    info = {}
    
    # Get attributes or main data
    attrs = data.get("attributes", data)
    
    # Basic info
    info["make"] = attrs.get("make")
    info["model"] = attrs.get("model")
    info["year"] = attrs.get("year")
    
    # Engine info
    info["engine"] = attrs.get("engine")
    info["engine_type"] = attrs.get("engine_type")
    info["fuel_type"] = attrs.get("fuel_type")
    info["displacement"] = attrs.get("displacement")
    
    # Transmission
    info["transmission"] = attrs.get("transmission")
    info["gears"] = attrs.get("gears")
    
    # Body
    info["body_type"] = attrs.get("body_type")
    info["doors"] = attrs.get("no_of_doors")
    info["seats"] = attrs.get("no_of_seats")
    
    # Dimensions
    info["length_mm"] = attrs.get("length_mm")
    info["width_mm"] = attrs.get("width_mm")
    info["height_mm"] = attrs.get("height_mm")
    
    # Performance
    info["max_speed"] = attrs.get("max_speed_kmh")
    info["co2_emission"] = attrs.get("avg_co2_emission_g_km")
    
    # Remove None values
    return {k: v for k, v in info.items() if v is not None}

async def main():
    print(f"Testing CarsXE API endpoints for VIN: {TEST_VIN}")
    print("=" * 60)
    
    # Test specs endpoint
    print("\n1. SPECS ENDPOINT (/specs)")
    print("-" * 40)
    specs_data = await test_endpoint("specs", TEST_VIN)
    
    if "error" in specs_data:
        print(f"Error: {specs_data['error']}")
    else:
        print(f"Success: {specs_data.get('success', 'N/A')}")
        field_count = count_fields(specs_data)
        print(f"Total non-empty fields: {field_count}")
        
        key_info = extract_key_info(specs_data)
        print("\nKey Information Found:")
        for key, value in key_info.items():
            print(f"  {key}: {value}")
        
        # Save for inspection
        with open("specs_response.json", "w") as f:
            json.dump(specs_data, f, indent=2)
        print("\nFull response saved to: specs_response.json")
    
    # Test international endpoint
    print("\n2. INTERNATIONAL ENDPOINT (/international)")
    print("-" * 40)
    intl_data = await test_endpoint("international", TEST_VIN)
    
    if "error" in intl_data:
        print(f"Error: {intl_data['error']}")
    else:
        print(f"Success: {intl_data.get('success', 'N/A')}")
        field_count = count_fields(intl_data)
        print(f"Total non-empty fields: {field_count}")
        
        key_info = extract_key_info(intl_data)
        print("\nKey Information Found:")
        for key, value in key_info.items():
            print(f"  {key}: {value}")
        
        # Save for inspection
        with open("international_response.json", "w") as f:
            json.dump(intl_data, f, indent=2)
        print("\nFull response saved to: international_response.json")
    
    # Compare unique fields
    print("\n3. COMPARISON")
    print("-" * 40)
    
    if "error" not in specs_data and "error" not in intl_data:
        specs_attrs = set(specs_data.get("attributes", {}).keys())
        intl_attrs = set(intl_data.get("attributes", {}).keys())
        
        specs_only = specs_attrs - intl_attrs
        intl_only = intl_attrs - specs_attrs
        common = specs_attrs & intl_attrs
        
        print(f"Common fields: {len(common)}")
        print(f"Specs-only fields: {len(specs_only)}")
        print(f"International-only fields: {len(intl_only)}")
        
        if specs_only:
            print("\nFields only in SPECS endpoint:")
            for field in sorted(list(specs_only)[:10]):  # Show first 10
                print(f"  - {field}")
            if len(specs_only) > 10:
                print(f"  ... and {len(specs_only) - 10} more")
        
        if intl_only:
            print("\nFields only in INTERNATIONAL endpoint:")
            for field in sorted(list(intl_only)[:10]):  # Show first 10
                print(f"  - {field}")
            if len(intl_only) > 10:
                print(f"  ... and {len(intl_only) - 10} more")

if __name__ == "__main__":
    asyncio.run(main())