#!/usr/bin/env python3
"""
Debug script to test the specific VIN that's causing issues
"""
import asyncio
import os
from dotenv import load_dotenv
from vinbot.carsxe_client import CarsXEClient
from vinbot.vin import is_valid_vin, normalize_vin

# Load environment variables
load_dotenv()

async def test_specific_vin():
    api_key = os.getenv("CARSXE_API_KEY")
    if not api_key:
        print("CARSXE_API_KEY not found in environment")
        return
    
    print(f"API Key: {api_key}")
    
    # Test with the specific VIN that's causing issues
    vin = "WBSJF0C50JB282102"
    
    print(f"VIN: {vin}")
    print(f"Is valid VIN: {is_valid_vin(vin)}")
    normalized = normalize_vin(vin)
    print(f"Normalized VIN: {normalized}")
    
    client = CarsXEClient(api_key=api_key)
    
    try:
        print(f"Attempting to decode VIN: {normalized}")
        data = await client.decode_vin(normalized)
        print("Success! Response data:")
        print(f"Make: {data.get('attributes', {}).get('make', 'N/A')}")
        print(f"Model: {data.get('attributes', {}).get('model', 'N/A')}")
        print(f"Year: {data.get('attributes', {}).get('year', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
        # Let's also check if this is a CarsXEError
        if "CarsXEError" in str(type(e)):
            print(f"CarsXEError details: {str(e)}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_specific_vin())