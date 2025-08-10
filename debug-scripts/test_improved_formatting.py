#!/usr/bin/env python3
"""
Test script to see how our improved Auto.dev data formatting works
"""

import asyncio
import json
import sys
import os

# Add the project root to the path so we can import vinbot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.autodev_client import AutoDevClient
from vinbot.formatter import format_vehicle_summary


async def test_improved_formatting():
    # Check if API key is provided
    api_key = os.getenv("AUTODEV_API_KEY")
    if not api_key:
        print("Error: AUTODEV_API_KEY environment variable not set")
        print("Please set it with: export AUTODEV_API_KEY='your-api-key'")
        return
    
    # Create Auto.dev client
    client = AutoDevClient(api_key=api_key)
    
    # Use the VIN that actually returns data
    vin = "1FTEW1E88HKE34785"  # 2017 Ford F-150
    
    print(f"Testing improved Auto.dev data formatting for VIN: {vin}")
    print("=" * 50)
    
    try:
        # Get the raw response from Auto.dev
        url = f"{AutoDevClient.BASE_URL}/vin/{vin.upper()}"
        print(f"Making request to: {url}")
        
        import httpx
        async with httpx.AsyncClient(timeout=15) as httpx_client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            }
            
            response = await httpx_client.get(url, headers=headers)
            
            if response.status_code == 200:
                raw_data = response.json()
                print("Raw API Response received successfully")
                
                # Test our improved format_response method
                print("\nFormatted Response with Improved Formatting:")
                print("-" * 45)
                formatted_data = client.format_response(raw_data)
                print(json.dumps(formatted_data, indent=2, default=str))
                
                print("\nTelegram Bot Output with Improved Formatting:")
                print("-" * 45)
                summary = format_vehicle_summary(formatted_data)
                print(summary)
                
                # Show what sections are now available
                print("\nAvailable Sections with Improved Formatting:")
                print("-" * 45)
                sections = []
                if "marketvalue" in formatted_data:
                    sections.append("Market Value")
                if "history" in formatted_data:
                    sections.append("History")
                if "recalls" in formatted_data:
                    sections.append("Recalls")
                if "attributes" in formatted_data and "features" in formatted_data["attributes"]:
                    sections.append("Features")
                    
                if sections:
                    print("Available sections:", ", ".join(sections))
                else:
                    print("No additional sections available")
                
            else:
                print(f"Error: API returned status {response.status_code}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_improved_formatting())