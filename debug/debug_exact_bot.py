#!/usr/bin/env python3
"""
Debug script that exactly replicates the bot's initialization and flow
"""
import asyncio
import os
from dotenv import load_dotenv
# CarsXE removed
from vinbot.vin import is_valid_vin, normalize_vin
from vinbot.config import load_settings
from vinbot.upstash_cache import UpstashCache

# Load environment variables
load_dotenv()

async def test_exact_bot_flow():
    # Load settings exactly like the bot does
    settings = load_settings()
    print(f"Settings loaded successfully")
    # No CarsXE key required
    
    # Initialize cache exactly like the bot does
    cache = None
    if os.getenv("UPSTASH_REDIS_REST_URL") and os.getenv("UPSTASH_REDIS_REST_TOKEN"):
        print("Initializing Upstash cache")
        cache = UpstashCache(ttl_seconds=settings.redis_ttl_seconds)
    # Redis removed
    else:
        print("No cache configured")
    
    # Initialize client exactly like the bot does
    from vinbot.nhtsa_client import NHTSAClient
    nhtsa_client = NHTSAClient(cache=cache, timeout=settings.http_timeout_seconds)
    
    # Test with the specific VIN that's causing issues
    vin = "WBSJF0C50JB282102"
    print(f"VIN: {vin}")
    print(f"Is valid VIN: {is_valid_vin(vin)}")
    normalized = normalize_vin(vin)
    print(f"Normalized VIN: {normalized}")
    
    try:
        print(f"Attempting to decode VIN: {normalized}")
        data = await nhtsa_client.decode_vin(normalized)
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
        # NHTSA client has no persistent client to close here
        pass

if __name__ == "__main__":
    asyncio.run(test_exact_bot_flow())