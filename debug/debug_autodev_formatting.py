#!/usr/bin/env python3
"""
Debug script to see how Auto.dev data is formatted in the Telegram bot
"""

import asyncio
import json
import sys
import os

# Add the project root to the path so we can import vinbot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.autodev_client import AutoDevClient
from vinbot.formatter import format_vehicle_summary


async def debug_autodev_formatting():
    # Check if API key is provided
    api_key = os.getenv("AUTODEV_API_KEY")
    if not api_key:
        print("Error: AUTODEV_API_KEY environment variable not set")
        print("Please set it with: export AUTODEV_API_KEY='your-api-key'")
        return
    
    # Create Auto.dev client
    client = AutoDevClient(api_key=api_key)
    
    # Use a sample VIN
    vin = "1HGBH41JXMN109186"  # 1995 Honda Accord (common test VIN)
    
    print(f"Debugging Auto.dev data formatting for VIN: {vin}")
    print("=" * 50)
    
    try:
        # Get formatted data from our client
        formatted_data = await client.decode_vin(vin)
        
        print("Formatted Data Structure:")
        print("-" * 30)
        print(json.dumps(formatted_data, indent=2, default=str))
        
        print("\nCurrent Telegram Bot Output:")
        print("-" * 30)
        summary = format_vehicle_summary(formatted_data)
        print(summary)
        
        # Check what additional sections are available
        print("\nAvailable Additional Sections:")
        print("-" * 30)
        sections = []
        if "marketvalue" in formatted_data:
            sections.append("Market Value")
        if "history" in formatted_data:
            sections.append("History")
        if "recalls" in formatted_data:
            sections.append("Recalls")
        if "features" in formatted_data["attributes"]:
            sections.append("Features")
        if "standard_equipment" in formatted_data["attributes"]:
            sections.append("Standard Equipment")
        if "optional_equipment" in formatted_data["attributes"]:
            sections.append("Optional Equipment")
            
        if sections:
            print("Available sections:", ", ".join(sections))
        else:
            print("No additional sections available")
            
        # Show raw data for analysis
        if "raw_data" in formatted_data:
            print("\nRaw Data Keys (for mapping improvements):")
            print("-" * 40)
            raw_data = formatted_data["raw_data"]
            for key in raw_data.keys():
                value = raw_data[key]
                if isinstance(value, (dict, list)):
                    print(f"  {key}: {type(value).__name__} ({len(value)} items)")
                else:
                    value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"  {key}: {value_str}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_autodev_formatting())