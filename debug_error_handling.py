#!/usr/bin/env python3
"""
Debug script to test the exact error handling in the bot
"""
import asyncio
import os
import logging
from dotenv import load_dotenv
from vinbot.carsxe_client import CarsXEClient, CarsXEError
from vinbot.vin import is_valid_vin, normalize_vin
from vinbot.config import load_settings
from vinbot.upstash_cache import UpstashCache
from vinbot.redis_cache import RedisCache

# Set up logging to match the bot
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

# Load environment variables
load_dotenv()

async def test_error_handling():
    # Load settings exactly like the bot does
    settings = load_settings()
    print(f"Settings loaded successfully")
    
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
        
        # Simulate the error message formatting like the bot does
        error_message = f"Error decoding VIN: CarsXE responded with 404: <!DOCTYPE html><html><head><meta charSet=\"utf-8\"/><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/><link rel=\"preload\" as=\"script\" fetchPriority=\"low\" href=\"/_next/static/chunks/we"
        print(f"\nIf we were to format an error like this, it would look like:")
        print(error_message[:200] + "...")
        
    except CarsXEError as e:
        print(f"CarsXEError caught: {e}")
        print(f"Error type: {type(e)}")
        
        # Simulate the error message formatting like the bot does
        error_message = f"Error decoding VIN: {e}"
        print(f"Formatted error message: {error_message}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Error type: {type(e)}")
        
        # Simulate the error message formatting like the bot does
        error_message = f"Error decoding VIN: {e}"
        print(f"Formatted error message: {error_message}")
    finally:
        await carsxe_client.aclose()

if __name__ == "__main__":
    asyncio.run(test_error_handling())