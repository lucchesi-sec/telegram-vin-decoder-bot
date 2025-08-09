#!/usr/bin/env python3
"""
Test all available CarsXE API endpoints to find the most detailed one
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Tuple
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("CARSXE_API_KEY")
if not API_KEY:
    print("Error: CARSXE_API_KEY not found in environment")
    exit(1)

TEST_VIN = "WDD2J6BB2KA047394"

# Known CarsXE endpoints based on documentation
ENDPOINTS = [
    ("specs", "Vehicle Specifications"),
    ("marketvalue", "Market Value"),
    ("history", "Vehicle History"),
    ("recalls", "Recalls"),
    ("images", "Vehicle Images"),
    ("decode", "VIN Decode"),
    ("vin", "VIN Info"),
    ("platedecoder", "Plate Decoder"),
]

async def test_endpoint(endpoint: str, vin: str) -> Tuple[str, Dict[str, Any]]:
    """Test a specific CarsXE API endpoint"""
    url = f"https://api.carsxe.com/{endpoint}"
    params = {
        "key": API_KEY,
        "vin": vin
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                return endpoint, response.json()
            else:
                return endpoint, {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return endpoint, {"error": str(e)}

def count_fields(data: Dict[str, Any], prefix: str = "") -> int:
    """Count non-null fields in the response"""
    count = 0
    if isinstance(data, dict):
        for key, value in data.items():
            if value is not None and value != "" and value != [] and value != {}:
                if isinstance(value, dict):
                    count += count_fields(value, f"{prefix}{key}.")
                elif isinstance(value, list) and len(value) > 0:
                    count += 1
                    # Count fields in list items if they're dicts
                    if isinstance(value[0], dict):
                        count += count_fields(value[0], f"{prefix}{key}[0].")
                else:
                    count += 1
    return count

def get_unique_fields(data: Dict[str, Any]) -> set:
    """Get all unique field names from response"""
    fields = set()
    
    def extract_fields(obj, prefix=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                fields.add(f"{prefix}{key}")
                if isinstance(value, dict):
                    extract_fields(value, f"{prefix}{key}.")
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    extract_fields(value[0], f"{prefix}{key}[].")
    
    extract_fields(data)
    return fields

async def main():
    print(f"Testing ALL CarsXE API endpoints for VIN: {TEST_VIN}")
    print("=" * 80)
    
    # Test all endpoints concurrently
    tasks = [test_endpoint(endpoint, TEST_VIN) for endpoint, _ in ENDPOINTS]
    results = await asyncio.gather(*tasks)
    
    successful_endpoints = []
    failed_endpoints = []
    
    for i, (endpoint, data) in enumerate(results):
        endpoint_name, description = ENDPOINTS[i]
        print(f"\n{i+1}. {description.upper()} (/{endpoint_name})")
        print("-" * 40)
        
        if "error" in data:
            print(f"❌ Failed: {data['error']}")
            failed_endpoints.append(endpoint_name)
        else:
            field_count = count_fields(data)
            print(f"✅ Success!")
            print(f"   Total non-empty fields: {field_count}")
            
            # Extract some key info if available
            attrs = data.get("attributes", data)
            if isinstance(attrs, dict):
                make = attrs.get("make")
                model = attrs.get("model")
                year = attrs.get("year")
                if make or model or year:
                    print(f"   Vehicle: {year} {make} {model}".strip())
            
            successful_endpoints.append((endpoint_name, field_count, data))
            
            # Save response for inspection
            filename = f"{endpoint_name}_response.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"   Response saved to: {filename}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if successful_endpoints:
        print(f"\n✅ Successful endpoints ({len(successful_endpoints)}):")
        # Sort by field count
        successful_endpoints.sort(key=lambda x: x[1], reverse=True)
        for endpoint, field_count, _ in successful_endpoints:
            print(f"   - /{endpoint}: {field_count} fields")
        
        # Find the most detailed endpoint
        best_endpoint, best_count, best_data = successful_endpoints[0]
        print(f"\n🏆 Most detailed endpoint: /{best_endpoint} with {best_count} fields")
        
        # Compare top endpoints
        if len(successful_endpoints) > 1:
            print("\n📊 Field comparison between top endpoints:")
            for i in range(min(3, len(successful_endpoints))):
                endpoint, count, data = successful_endpoints[i]
                fields = get_unique_fields(data)
                print(f"   {i+1}. /{endpoint}: {len(fields)} unique field paths")
                
                # Show some unique fields
                if i == 0:
                    baseline_fields = fields
                else:
                    unique_to_this = fields - baseline_fields
                    if unique_to_this:
                        print(f"      Unique fields: {', '.join(list(unique_to_this)[:5])}")
                        if len(unique_to_this) > 5:
                            print(f"      ... and {len(unique_to_this) - 5} more")
    
    if failed_endpoints:
        print(f"\n❌ Failed endpoints ({len(failed_endpoints)}):")
        for endpoint in failed_endpoints:
            print(f"   - /{endpoint}")

if __name__ == "__main__":
    asyncio.run(main())