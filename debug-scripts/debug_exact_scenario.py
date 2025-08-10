#!/usr/bin/env python3
"""
Debug script to test the exact scenario from the error report
"""
import asyncio
import os
from dotenv import load_dotenv
# CarsXE removed
from vinbot.vin import is_valid_vin, normalize_vin

# Load environment variables
load_dotenv()

async def test_exact_scenario():
    api_key = os.getenv("CARSXE_API_KEY")
    if not api_key:
        print("CARSXE_API_KEY not found in environment")
        return
    
    print(f"API Key: {api_key}")
    
    # Test the exact scenario from the error report
    # User sent "/vin vin" - so the VIN parameter is "vin"
    vin_param = "vin"
    print(f"VIN parameter from command: '{vin_param}'")
    
    # This is what happens in the bot:
    normalized = normalize_vin(vin_param)
    print(f"After normalization: '{normalized}'")
    
    is_valid = is_valid_vin(normalized)
    print(f"Is valid VIN: {is_valid}")
    
    if not is_valid:
        print("Bot should have rejected this VIN and not attempted to decode it")
        return
    
    # If for some reason the validation passed, let's see what happens
    print("Attempting to decode anyway...")
    # CarsXE removed
    
    try:
        data = await client.decode_vin(normalized)
        print("Success! Response data:")
        print(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_exact_scenario())