#!/usr/bin/env python3
"""
Debug script that exactly replicates the bot's initialization and flow
"""
import asyncio
import os
from dotenv import load_dotenv
from vinbot.carsxe_client import CarsXEClient, CarsXEError
from vinbot.vin import is_valid_vin, normalize_vin
from vinbot.config import load_settings
from vinbot.upstash_cache import UpstashCache
from vinbot.redis_cache import RedisCache

# Load environment variables
load_dotenv()

async def test_exact_bot_flow():
    # Load settings exactly like the bot does
    settings = load_settings()
    print(f"Settings loaded successfully")
    print(f"API Key: {settings.carsxe_api_key[:5]}...{settings.carsxe_api_key[-5:]}")
    
    # Initialize cache exactly like the bot does
    cache = None
    if os.getenv("UPSTASH_REDIS_REST_URL") and os.getenv("UPSTASH_REDIS_REST_TOKEN"):
        print("Initializing Upstash cache")
        cache = UpstashCache(ttl_seconds=settings.redis_ttl_seconds)
    elif settings.redis_url:
        print("Initializing Redis cache")
        cache = RedisCache(redis_url=settings.redis_url, ttl_seconds=settings.redis_ttl_seconds)
    else:
        print("No cache configured")
    
    # Initialize client exactly like the bot does
    carsxe_client = CarsXEClient(
        api_key=settings.carsxe_api_key,
        timeout_seconds=settings.http_timeout_seconds,
        cache=cache
    )
    
    # Test with the specific VIN that's causing issues
    vin = "WBSJF0C50JB282102"
    print(f"VIN: {vin}")
    print(f"Is valid VIN: {is_valid_vin(vin)}")
    normalized = normalize_vin(vin)
    print(f"Normalized VIN: {normalized}")
    
    try:
        print(f"Attempting to decode VIN: {normalized}")
        data = await carsxe_client.decode_vin(normalized)
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
        await carsxe_client.aclose()

if __name__ == "__main__":
    asyncio.run(test_exact_bot_flow())