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
    
    # Use the VIN that actually returns data
    vin = "1FTEW1E88HKE34785"  # 2017 Ford F-150
    
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
        
        # Analyze what's missing from our current formatting
        print("\nAnalysis of Missing Information:")
        print("-" * 35)
        analyze_missing_info(formatted_data)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def analyze_missing_info(formatted_data):
    """Analyze what information from the raw data is not being included in the formatted output"""
    raw_data = formatted_data.get("raw_data", {})
    attributes = formatted_data.get("attributes", {})
    
    print("1. Engine Information:")
    engine = raw_data.get("engine", {})
    if engine:
        print(f"   - Horsepower: {engine.get('horsepower')}")
        print(f"   - Torque: {engine.get('torque')}")
        print(f"   - Cylinders: {engine.get('cylinder')}")
        print(f"   - Size: {engine.get('size')}L")
        print(f"   - Fuel Type: {engine.get('fuelType')}")
        print(f"   - Configuration: {engine.get('configuration')}")
        print(f"   - Compression Ratio: {engine.get('compressionRatio')}")
        print(f"   - Total Valves: {engine.get('totalValves')}")
        print(f"   - Type: {engine.get('type')}")
        print(f"   - Compressor Type: {engine.get('compressorType')}")
    
    print("\n2. Transmission Information:")
    transmission = raw_data.get("transmission", {})
    if transmission:
        print(f"   - Type: {transmission.get('transmissionType')}")
        print(f"   - Number of Speeds: {transmission.get('numberOfSpeeds')}")
        print(f"   - Automatic Type: {transmission.get('automaticType')}")
    
    print("\n3. Drive and Body Information:")
    print(f"   - Driven Wheels: {raw_data.get('drivenWheels')}")
    print(f"   - Number of Doors: {raw_data.get('numOfDoors')}")
    print(f"   - Primary Body Type: {raw_data.get('categories', {}).get('primaryBodyType')}")
    print(f"   - Vehicle Style: {raw_data.get('categories', {}).get('vehicleStyle')}")
    print(f"   - Vehicle Size: {raw_data.get('categories', {}).get('vehicleSize')}")
    print(f"   - EPA Class: {raw_data.get('categories', {}).get('epaClass')}")
    
    print("\n4. Fuel Economy:")
    mpg = raw_data.get("mpg", {})
    if mpg:
        print(f"   - City MPG: {mpg.get('city')}")
        print(f"   - Highway MPG: {mpg.get('highway')}")
    
    print("\n5. Options and Features:")
    options = raw_data.get("options", [])
    if options:
        print(f"   - Number of Option Categories: {len(options)}")
        for category in options[:3]:  # Show first 3 categories
            print(f"   - Category: {category.get('category')}")
            opts = category.get('options', [])
            print(f"     - Number of Options: {len(opts)}")
            if opts:
                print(f"     - Sample Option: {opts[0].get('name')}")
    
    print("\n6. Colors:")
    colors = raw_data.get("colors", [])
    if colors:
        print(f"   - Number of Color Categories: {len(colors)}")
        for category in colors:
            print(f"   - Category: {category.get('category')}")
            color_opts = category.get('options', [])
            print(f"     - Number of Colors: {len(color_opts)}")
            if color_opts:
                print(f"     - Sample Color: {color_opts[0].get('name')}")
    
    print("\n7. Model and Trim Information:")
    years = raw_data.get("years", [])
    if years:
        year_info = years[0]
        print(f"   - Year: {year_info.get('year')}")
        styles = year_info.get('styles', [])
        if styles:
            style = styles[0]
            print(f"   - Style Name: {style.get('name')}")
            print(f"   - Trim: {style.get('trim')}")
            submodel = style.get('submodel', {})
            print(f"   - Body: {submodel.get('body')}")
            print(f"   - Model Name: {submodel.get('modelName')}")


if __name__ == "__main__":
    asyncio.run(debug_autodev_formatting())