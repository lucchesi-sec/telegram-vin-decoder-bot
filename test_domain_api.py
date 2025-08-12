#!/usr/bin/env python
"""Test the domain API functionality."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.dependencies import Container
from src.domain.user.value_objects.user_preferences import UserPreferences

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_decode():
    """Test VIN decoding with the application service."""
    # Initialize container
    container = Container()
    
    # Bootstrap command/query buses
    Container.bootstrap(container)
    
    # Get vehicle service
    vehicle_service = container.vehicle_application_service()
    
    # Create test preferences
    preferences = UserPreferences(
        preferred_decoder="nhtsa",
        language="en"
    )
    
    # Test VIN
    test_vin = "1HGBH41JXMN109186"
    
    try:
        print(f"Testing VIN decode for: {test_vin}")
        result = await vehicle_service.decode_vin(
            vin=test_vin,
            user_preferences=preferences,
            force_refresh=False
        )
        
        print(f"Success! Decoded VIN:")
        print(f"  Manufacturer: {result.manufacturer}")
        print(f"  Model: {result.model}")
        print(f"  Year: {result.model_year}")
        print(f"  Service Used: {result.service_used}")
        print(f"  Attributes: {result.attributes}")
        
    except Exception as e:
        print(f"Error decoding VIN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_decode())