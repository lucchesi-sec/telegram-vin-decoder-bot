#!/usr/bin/env python3
"""
Debug script to test the exact flow used by the Telegram bot
"""
import asyncio
import os
from dotenv import load_dotenv
# CarsXE removed
from vinbot.vin import is_valid_vin, normalize_vin

# Load environment variables
load_dotenv()

async def test_bot_flow():
    api_key = os.getenv("CARSXE_API_KEY")
    if not api_key:
        print("CARSXE_API_KEY not found in environment")
        return
    
    print(f"API Key: {api_key}")
    
    # Test with a VIN that might be causing issues
    # Let's try a few different VINs
    test_vins = [
        "1HGBH41JXMN109186",  # Valid VIN
        "2T1BURHE5JC012345",  # Another valid VIN
    ]
    
    # CarsXE removed
    
    for vin in test_vins:
        print(f"\n--- Testing VIN: {vin} ---")
        print(f"Is valid VIN: {is_valid_vin(vin)}")
        normalized = normalize_vin(vin)
        print(f"Normalized VIN: {normalized}")
        
        try:
            print(f"Attempting to decode VIN: {normalized}")
            data = await client.decode_vin(normalized)
            print("Success! Response data:")
            print(f"Make: {data.get('attributes', {}).get('make', 'N/A')}")
            print(f"Model: {data.get('attributes', {}).get('model', 'N/A')}")
            print(f"Year: {data.get('attributes', {}).get('year', 'N/A')}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test with a VIN that might be causing the specific issue
    # Let's try to reproduce the exact error from the bot
    problematic_vin = "vin"  # This is what was mentioned in the error report
    print(f"\n--- Testing problematic VIN: '{problematic_vin}' ---")
    print(f"Is valid VIN: {is_valid_vin(problematic_vin)}")
    normalized = normalize_vin(problematic_vin)
    print(f"Normalized VIN: {normalized}")
    
    if is_valid_vin(normalized):
        try:
            print(f"Attempting to decode VIN: {normalized}")
            data = await client.decode_vin(normalized)
            print("Success! Response data:")
            print(data)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("VIN is not valid, skipping decode attempt")
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_bot_flow())