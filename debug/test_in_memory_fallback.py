#!/usr/bin/env python3
"""
Test script to verify the in-memory fallback functionality in UserDataManager
"""

import asyncio
import sys
import os

# Add the project root to the path so we can import vinbot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.user_data import UserDataManager


async def test_in_memory_fallback():
    print("Testing in-memory fallback functionality...")
    
    # Create UserDataManager without cache (None)
    user_data_mgr = UserDataManager(cache=None)
    
    user_id = 12345
    vin = "1HGBH41JXMN109186"
    vehicle_data = {
        "attributes": {
            "vin": vin,
            "year": "2020",
            "make": "Honda",
            "model": "Accord"
        }
    }
    
    # Test setting user service
    print("1. Testing set_user_service...")
    result = await user_data_mgr.set_user_service(user_id, "AutoDev")
    print(f"   Result: {result}")
    assert result == True, "set_user_service should return True"
    
    # Test getting user settings
    print("2. Testing get_user_settings...")
    settings = await user_data_mgr.get_user_settings(user_id)
    print(f"   Settings: {settings}")
    assert settings["service"] == "AutoDev", "Service should be AutoDev"
    
    # Test setting API key
    print("3. Testing set_user_api_key...")
    result = await user_data_mgr.set_user_api_key(user_id, "AutoDev", "test-api-key")
    print(f"   Result: {result}")
    assert result == True, "set_user_api_key should return True"
    
    # Test getting user settings with API key
    print("4. Testing get_user_settings with API key...")
    settings = await user_data_mgr.get_user_settings(user_id)
    print(f"   Settings: {settings}")
    assert settings["autodev_api_key"] == "test-api-key", "AutoDev API key should be set"
    
    # Test adding to history
    print("5. Testing add_to_history...")
    result = await user_data_mgr.add_to_history(user_id, vin, vehicle_data)
    print(f"   Result: {result}")
    assert result == True, "add_to_history should return True"
    
    # Test getting history
    print("6. Testing get_history...")
    history = await user_data_mgr.get_history(user_id)
    print(f"   History: {history}")
    assert len(history) == 1, "History should contain one entry"
    assert history[0][0] == vin, "History should contain the correct VIN"
    
    # Test adding to favorites
    print("7. Testing add_to_favorites...")
    result = await user_data_mgr.add_to_favorites(user_id, vin, vehicle_data, "My Honda")
    print(f"   Result: {result}")
    assert result == True, "add_to_favorites should return True"
    
    # Test getting favorites
    print("8. Testing get_favorites...")
    favorites = await user_data_mgr.get_favorites(user_id)
    print(f"   Favorites: {favorites}")
    assert len(favorites) == 1, "Favorites should contain one entry"
    assert favorites[0][0] == vin, "Favorites should contain the correct VIN"
    
    print("\nAll tests passed! In-memory fallback is working correctly.")


if __name__ == "__main__":
    asyncio.run(test_in_memory_fallback())