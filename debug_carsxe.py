#!/usr/bin/env python3
"""
Debug script to test CarsXE API access
"""
import asyncio
import os
from dotenv import load_dotenv
from vinbot.carsxe_client import CarsXEClient

# Load environment variables
load_dotenv()

async def test_carsxe():
    api_key = os.getenv("CARSXE_API_KEY")
    if not api_key:
        print("CARSXE_API_KEY not found in environment")
        return
    
    print(f"API Key: {api_key}")
    
    # Test with a valid VIN
    vin = "1HGBH41JXMN109186"
    
    client = CarsXEClient(api_key=api_key)
    
    try:
        print(f"Attempting to decode VIN: {vin}")
        data = await client.decode_vin(vin)
        print("Success! Response data:")
        print(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_carsxe())