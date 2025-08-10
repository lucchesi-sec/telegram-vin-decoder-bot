#!/usr/bin/env python3
"""
Improved formatter for Auto.dev data
"""

import asyncio
import json
import sys
import os

# Add the project root to the path so we can import vinbot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.autodev_client import AutoDevClient
from vinbot.formatter import format_vehicle_summary, format_vehicle_card


async def test_improved_formatter():
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
    
    print(f"Testing improved formatter for Auto.dev data for VIN: {vin}")
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
                
                # Format with our improved formatter
                formatted_data = client.format_response(raw_data)
                
                print("\nImproved Formatter Output:")
                print("-" * 30)
                improved_summary = format_improved_summary(formatted_data)
                print(improved_summary)
                
            else:
                print(f"Error: API returned status {response.status_code}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def format_improved_summary(data: dict) -> str:
    """Improved formatter specifically for Auto.dev data"""
    attrs = data.get("attributes", {})
    
    if not attrs:
        return "Could not parse vehicle data from response."
    
    lines = []
    
    # Header with vehicle information
    year = attrs.get("year", "")
    make = attrs.get("make", "")
    model = attrs.get("model", "")
    trim = attrs.get("trim", "")
    
    vehicle_desc = " ".join(str(v) for v in [year, make, model, trim] if v)
    lines.append(f"🚗 **{vehicle_desc}**")
    lines.append("=" * len(vehicle_desc) if len(vehicle_desc) < 50 else "=" * 50)
    
    # Engine Information
    lines.append("\n🔧 **ENGINE SPECIFICATIONS**")
    lines.append("-" * 25)
    
    engine_fields = [
        ("Engine", attrs.get("engine")),
        ("Configuration", attrs.get("configuration")),
        ("Cylinders", attrs.get("cylinders")),
        ("Displacement", f"{attrs.get('displacement')}L" if attrs.get("displacement") else None),
        ("Fuel Type", attrs.get("fuel_type")),
        ("Horsepower", f"{attrs.get('horsepower')} hp" if attrs.get("horsepower") else None),
        ("Torque", f"{attrs.get('torque')} lb-ft" if attrs.get("torque") else None),
        ("Compressor", attrs.get("compressor_type")),
    ]
    
    for label, value in engine_fields:
        if value:
            lines.append(f"**{label}:** {value}")
    
    # Transmission Information
    lines.append("\n⚙️ **TRANSMISSION**")
    lines.append("-" * 18)
    
    transmission_fields = [
        ("Type", attrs.get("transmission_type")),
        ("Name", attrs.get("transmission")),
        ("Speeds", attrs.get("number_of_speeds")),
        ("Automatic Type", attrs.get("automatic_type")),
    ]
    
    for label, value in transmission_fields:
        if value:
            lines.append(f"**{label}:** {value}")
    
    # Body and Drive Information
    lines.append("\n🚚 **BODY & DRIVE**")
    lines.append("-" * 17)
    
    body_fields = [
        ("Body Type", attrs.get("body_type")),
        ("Vehicle Style", attrs.get("vehicle_style")),
        ("Drive Type", attrs.get("drive_type")),
        ("Doors", attrs.get("doors")),
        ("Vehicle Size", attrs.get("vehicle_size")),
        ("EPA Class", attrs.get("epa_class")),
    ]
    
    for label, value in body_fields:
        if value:
            lines.append(f"**{label}:** {value}")
    
    # Fuel Economy
    mpg_city = attrs.get("mpg_city")
    mpg_highway = attrs.get("mpg_highway")
    if mpg_city or mpg_highway:
        lines.append("\n⛽ **FUEL ECONOMY**")
        lines.append("-" * 18)
        if mpg_city:
            lines.append(f"**City:** {mpg_city} MPG")
        if mpg_highway:
            lines.append(f"**Highway:** {mpg_highway} MPG")
    
    # Features (limit to first 10 for readability)
    features = attrs.get("features", [])
    if features:
        lines.append("\n✨ **FEATURES** (Sample)")
        lines.append("-" * 22)
        for feature in features[:10]:  # Limit to first 10
            lines.append(f"• {feature}")
        if len(features) > 10:
            lines.append(f"... and {len(features) - 10} more features")
    
    # Colors (limit to first 5 for readability)
    colors = attrs.get("colors", [])
    if colors:
        lines.append("\n🎨 **AVAILABLE COLORS** (Sample)")
        lines.append("-" * 30)
        for color in colors[:5]:  # Limit to first 5
            lines.append(f"• {color}")
        if len(colors) > 5:
            lines.append(f"... and {len(colors) - 5} more colors")
    
    return "\n".join(lines)


if __name__ == "__main__":
    asyncio.run(test_improved_formatter())