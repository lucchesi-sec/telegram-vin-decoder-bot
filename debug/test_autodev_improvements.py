#!/usr/bin/env python3
"""
Comprehensive test of Auto.dev improvements in bot context
"""

import asyncio
import sys
import os

# Add the project root to the path so we can import vinbot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.autodev_client import AutoDevClient


async def test_autodev_improvements():
    # Check if API key is provided
    api_key = os.getenv("AUTODEV_API_KEY")
    if not api_key:
        print("Error: AUTODEV_API_KEY environment variable not set")
        print("Please set it with: export AUTODEV_API_KEY='your-api-key'")
        return
    
    print("Testing Auto.dev improvements in bot context")
    print("=" * 50)
    
    # Create Auto.dev client
    client = AutoDevClient(api_key=api_key)
    
    # Use the VIN that actually returns data
    vin = "1FTEW1E88HKE34785"  # 2017 Ford F-150
    
    print(f"Testing with VIN: {vin}")
    
    try:
        # Test the full decode process
        print("\n1. Testing VIN decode process...")
        formatted_data = await client.decode_vin(vin)
        print("   ✓ VIN decoded successfully")
        
        # Check that we have the expected structure
        assert formatted_data["success"] == True, "Decode should be successful"
        assert "attributes" in formatted_data, "Should have attributes"
        assert formatted_data["service"] == "AutoDev", "Service should be AutoDev"
        print("   ✓ Data structure is correct")
        
        # Check that we have key information
        attrs = formatted_data["attributes"]
        assert "make" in attrs and attrs["make"] == "Ford", "Should have correct make"
        assert "model" in attrs and attrs["model"] == "F-150", "Should have correct model"
        assert "year" in attrs and attrs["year"] == 2017, "Should have correct year"
        assert "engine" in attrs, "Should have engine information"
        assert "transmission" in attrs, "Should have transmission information"
        assert "features" in attrs, "Should have features list"
        assert "colors" in attrs, "Should have colors list"
        print("   ✓ Key information extracted correctly")
        
        # Test formatting
        print("\n2. Testing data formatting...")
        from vinbot.formatter import format_vehicle_summary, format_vehicle_card
        from vinbot.formatter_extensions import format_market_value, format_history
        
        summary = format_vehicle_summary(formatted_data)
        assert "Ford F-150" in summary, "Summary should contain vehicle description"
        assert "ENGINE SPECIFICATIONS" in summary, "Summary should have engine section"
        assert "TRANSMISSION" in summary, "Summary should have transmission section"
        print("   ✓ Summary formatting works correctly")
        
        card = format_vehicle_card(formatted_data)
        assert "Ford" in card, "Card should contain make"
        assert "F-150" in card, "Card should contain model"
        print("   ✓ Card formatting works correctly")
        
        # Test extensions
        market_value = format_market_value(formatted_data)
        assert "MARKET VALUE" in market_value, "Market value should be formatted"
        print("   ✓ Market value formatting works correctly")
        
        history = format_history(formatted_data)
        assert "VEHICLE HISTORY" in history, "History should be formatted"
        print("   ✓ History formatting works correctly")
        
        print("\n3. Testing API key validation...")
        # Test valid key
        valid_key = "ZrQEPSkKZW56b0BmbWlhdXRvLmNvbQ=="
        assert client.validate_api_key(valid_key) == True, "Valid key should pass validation"
        print("   ✓ Valid API key validation works")
        
        # Test invalid key
        invalid_key = "invalid-key"
        assert client.validate_api_key(invalid_key) == False, "Invalid key should fail validation"
        print("   ✓ Invalid API key validation works")
        
        print("\n🎉 All Auto.dev improvements are working correctly!")
        print("\nSummary of improvements:")
        print("  ✓ Better data extraction from Auto.dev API")
        print("  ✓ Improved formatting for Auto.dev data")
        print("  ✓ Proper handling of engine, transmission, and body information")
        print("  ✓ Feature and color lists properly extracted")
        print("  ✓ Service-specific formatting in all formatter functions")
        print("  ✓ API key validation works correctly")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_autodev_improvements())
    if success:
        print("\n✅ All tests passed! Auto.dev improvements are ready for use.")
    else:
        print("\n❌ Some tests failed. Please check the output above.")