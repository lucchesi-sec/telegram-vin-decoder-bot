#!/usr/bin/env python3
"""
Debug script to test the exact flow the bot uses with caching
"""
import asyncio
import os
from dotenv import load_dotenv
# CarsXE removed
from vinbot.vin import is_valid_vin, normalize_vin
from vinbot.upstash_cache import UpstashCache
from vinbot.upstash_cache import UpstashCache

# Load environment variables
load_dotenv()

async def test_bot_flow_with_caching():
    # CarsXE removed
    
    # Test with the specific VIN that's causing issues
    vin = "WBSJF0C50JB282102"
    
    print(f"VIN: {vin}")
    print(f"Is valid VIN: {is_valid_vin(vin)}")
    normalized = normalize_vin(vin)
    print(f"Normalized VIN: {normalized}")
    
    # Initialize cache - prefer Upstash if configured
    cache = None
    if os.getenv("UPSTASH_REDIS_REST_URL") and os.getenv("UPSTASH_REDIS_REST_TOKEN"):
        print("Using Upstash cache")
        cache = UpstashCache(ttl_seconds=86400)
    else:
        print("No cache configured")
    
    # CarsXE removed
    
    try:
        print(f"Attempting to decode VIN: {normalized}")
        # Use NHTSA for debugging
        from vinbot.nhtsa_client import NHTSAClient
        nhtsa = NHTSAClient(cache=cache)
        data = await nhtsa.decode_vin(normalized)
        print("Success! Response data:")
        print(f"Make: {data.get('attributes', {}).get('make', 'N/A')}")
        print(f"Model: {data.get('attributes', {}).get('model', 'N/A')}")
        print(f"Year: {data.get('attributes', {}).get('year', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Error type: {type(e)}")
    finally:
        pass

if __name__ == "__main__":
    asyncio.run(test_bot_flow_with_caching())