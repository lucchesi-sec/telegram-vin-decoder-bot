#!/usr/bin/env python3
"""
Test the complete VIN decode with all endpoints
"""

import asyncio
import json
from dotenv import load_dotenv
import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# CarsXE removed
from vinbot.formatter import format_vehicle_summary
from vinbot.formatter_extensions import format_market_value, format_history

# Load environment
load_dotenv()

API_KEY = os.getenv("CARSXE_API_KEY")
TEST_VIN = "WDD2J6BB2KA047394"

async def main():
    print(f"Testing full VIN decode for: {TEST_VIN}")
    print("=" * 60)
    
    # Create client
    # CarsXE removed
    
    try:
        # Decode VIN (this now fetches all endpoints)
        print("\nFetching data from all endpoints...")
        data = await client.decode_vin(TEST_VIN)
        
        # Check what we got
        print("\n✅ Data retrieved successfully!")
        print(f"Has specs: {'attributes' in data}")
        print(f"Has history: {'history' in data and data['history']}")
        print(f"Has market value: {'marketvalue' in data and data['marketvalue']}")
        
        # Test main formatter
        print("\n" + "=" * 60)
        print("MAIN SUMMARY:")
        print("=" * 60)
        summary = format_vehicle_summary(data)
        print(summary)
        
        # Test market value formatter
        if 'marketvalue' in data and data['marketvalue']:
            print("\n" + "=" * 60)
            print("MARKET VALUE:")
            print("=" * 60)
            market = format_market_value(data)
            print(market)
        
        # Test history formatter
        if 'history' in data and data['history']:
            print("\n" + "=" * 60)
            print("HISTORY:")
            print("=" * 60)
            history = format_history(data)
            print(history)
        
        # Save full response for inspection
        with open("full_decode_response.json", "w") as f:
            json.dump(data, f, indent=2)
        print("\n✅ Full response saved to: full_decode_response.json")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())