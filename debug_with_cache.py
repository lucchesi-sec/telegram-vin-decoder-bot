#!/usr/bin/env python3
"""
Debug script to test the exact flow the bot uses with caching
"""
import asyncio
import os
from dotenv import load_dotenv
from vinbot.carsxe_client import CarsXEClient, CarsXEError
from vinbot.vin import is_valid_vin, normalize_vin
from vinbot.upstash_cache import UpstashCache
from vinbot.redis_cache import RedisCache

# Load environment variables
load_dotenv()

async def test_bot_flow_with_caching():
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
    
    # Initialize cache - prefer Upstash if configured, otherwise Redis
    cache = None
    if os.getenv("UPSTASH_REDIS_REST_URL") and os.getenv("UPSTASH_REDIS_REST_TOKEN"):
        print("Using Upstash cache")
        cache = UpstashCache(ttl_seconds=86400)
    elif os.getenv("REDIS_URL"):
        print("Using Redis cache")
        cache = RedisCache(ttl_seconds=86400)
    else:
        print("No cache configured")
    
    client = CarsXEClient(api_key=api_key, cache=cache)
    
    try:
        print(f"Attempting to decode VIN: {normalized}")
        data = await client.decode_vin(normalized)
        print("Success! Response data:")
        print(f"Make: {data.get('attributes', {}).get('make', 'N/A')}")
        print(f"Model: {data.get('attributes', {}).get('model', 'N/A')}")
        print(f"Year: {data.get('attributes', {}).get('year', 'N/A')}")
    except CarsXEError as e:
        print(f"CarsXEError: {e}")
        print(f"Error type: {type(e)}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Error type: {type(e)}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_bot_flow_with_caching())