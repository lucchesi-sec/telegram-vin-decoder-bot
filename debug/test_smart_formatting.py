#!/usr/bin/env python3
"""
Test script for the new smart formatting system

This script validates:
- Progressive disclosure levels
- Mobile vs desktop formatting
- User context adaptation
- Keyboard generation
"""

import asyncio
import sys
import os

# Add the project root to the path so we can import vinbot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.smart_formatter import (
    format_vehicle_smart_card, 
    InformationLevel, 
    DisplayMode,
    get_available_disclosure_levels,
    suggest_information_level,
    format_level_preview
)
from vinbot.smart_keyboards import (
    get_adaptive_keyboard,
    get_mobile_optimized_keyboard,
    get_desktop_optimized_keyboard,
    create_level_transition_message
)
from vinbot.user_context import UserContextManager


def create_sample_nhtsa_data():
    """Create sample NHTSA data for testing"""
    return {
        "attributes": {
            "vin": "1HGBH41JXMN109186",
            "year": "2021",
            "make": "Honda", 
            "model": "Accord",
            "body": "4-Door Sedan",
            "fuel_type": "Gasoline",
            "gears": "CVT",
            "drive": "FWD",
            "manufacturer": "Honda Motor Co., Ltd.",
            "plant_country": "United States",
            "length_mm": "4906",
            "width_mm": "1862", 
            "height_mm": "1450",
            "weight_empty_kg": "1442",
            "max_speed_kmh": "210",
            "no_of_doors": "4",
            "no_of_seats": "5",
            "abs": "Standard"
        },
        "service": "NHTSA"
    }


def create_sample_autodev_data():
    """Create sample Auto.dev data for testing"""
    return {
        "attributes": {
            "vin": "1FTEW1E88HKE34785",
            "year": "2017",
            "make": "Ford",
            "model": "F-150",
            "trim": "XL",
            "body_type": "Crew Cab Pickup",
            "fuel_type": "flex-fuel (unleaded/E85)",
            "drive_type": "four wheel drive",
            "doors": "4",
            "engine": "3.5l V6",
            "cylinders": 6,
            "displacement": 3.5,
            "horsepower": 282,
            "torque": 253,
            "transmission": "6A",
            "mpg_city": "17",
            "mpg_highway": "23",
            "features": [
                "Air Conditioning",
                "Power Steering", 
                "Power Brakes",
                "Power Door Locks",
                "Power Windows",
                "Tilt Wheel",
                "AM/FM Stereo",
                "Dual Air Bags",
                "Side Air Bags",
                "Steel Wheels",
                "Conventional Spare Tire"
            ]
        },
        "service": "AutoDev",
        "marketvalue": {
            "retail": 34775,
            "tradeIn": 33690,
            "msrp": 79900
        },
        "history": {
            "brandsRecordCount": 0
        }
    }


async def test_progressive_disclosure():
    """Test progressive disclosure levels"""
    print("🔍 Testing Progressive Disclosure Levels")
    print("=" * 50)
    
    # Test with NHTSA data
    nhtsa_data = create_sample_nhtsa_data()
    
    print("\n📋 NHTSA Data Testing:")
    print("-" * 25)
    
    for level in InformationLevel:
        print(f"\n{level.name} Level:")
        print(format_level_preview(level))
        formatted = format_vehicle_smart_card(nhtsa_data, level, DisplayMode.DESKTOP)
        lines = formatted.split('\n')
        print(f"Lines: {len(lines)}")
        print("Preview:")
        print('\n'.join(lines[:5]) + ("..." if len(lines) > 5 else ""))
    
    # Test with Auto.dev data
    autodev_data = create_sample_autodev_data()
    
    print("\n\n🚗 Auto.dev Data Testing:")
    print("-" * 25)
    
    for level in InformationLevel:
        print(f"\n{level.name} Level:")
        formatted = format_vehicle_smart_card(autodev_data, level, DisplayMode.DESKTOP)
        lines = formatted.split('\n')
        print(f"Lines: {len(lines)}")
        print("Preview:")
        print('\n'.join(lines[:5]) + ("..." if len(lines) > 5 else ""))


async def test_mobile_vs_desktop():
    """Test mobile vs desktop formatting"""
    print("\n\n📱 Testing Mobile vs Desktop Formatting")
    print("=" * 50)
    
    data = create_sample_autodev_data()
    
    print("\nMobile Format (Standard Level):")
    print("-" * 30)
    mobile_format = format_vehicle_smart_card(data, InformationLevel.STANDARD, DisplayMode.MOBILE)
    lines = mobile_format.split('\n')
    print(f"Total lines: {len(lines)}")
    max_line_length = max(len(line.replace('*', '').replace('`', '')) for line in lines if line.strip())
    print(f"Max line length: {max_line_length} chars")
    print("\nPreview:")
    print(mobile_format[:300] + "..." if len(mobile_format) > 300 else mobile_format)
    
    print("\n\nDesktop Format (Standard Level):")
    print("-" * 30)
    desktop_format = format_vehicle_smart_card(data, InformationLevel.STANDARD, DisplayMode.DESKTOP)
    lines = desktop_format.split('\n')
    print(f"Total lines: {len(lines)}")
    max_line_length = max(len(line.replace('*', '').replace('`', '')) for line in lines if line.strip())
    print(f"Max line length: {max_line_length} chars")
    print("\nPreview:")
    print(desktop_format[:300] + "..." if len(desktop_format) > 300 else desktop_format)


async def test_keyboard_generation():
    """Test adaptive keyboard generation"""
    print("\n\n⌨️ Testing Keyboard Generation")
    print("=" * 50)
    
    data = create_sample_autodev_data()
    vin = "1FTEW1E88HKE34785"
    
    # Test mobile keyboard
    print("\nMobile Keyboard:")
    print("-" * 15)
    mobile_kb = get_mobile_optimized_keyboard(vin, has_history=True, has_marketvalue=True)
    for row in mobile_kb.inline_keyboard:
        buttons = [btn.text for btn in row]
        print(f"Row: {buttons}")
    
    # Test desktop keyboard  
    print("\nDesktop Keyboard:")
    print("-" * 15)
    available_levels = get_available_disclosure_levels(data)
    desktop_kb = get_desktop_optimized_keyboard(
        vin, 
        InformationLevel.STANDARD, 
        available_levels,
        has_history=True, 
        has_marketvalue=True
    )
    for row in desktop_kb.inline_keyboard:
        buttons = [btn.text for btn in row]
        print(f"Row: {buttons}")
    
    # Test adaptive keyboard
    print("\nAdaptive Keyboard (Mobile Context):")
    print("-" * 30)
    user_context = {"is_mobile": True, "frequent_user": False}
    adaptive_kb = get_adaptive_keyboard(vin, data, InformationLevel.STANDARD, user_context)
    for row in adaptive_kb.inline_keyboard:
        buttons = [btn.text for btn in row]
        print(f"Row: {buttons}")


async def test_user_context():
    """Test user context management"""
    print("\n\n👤 Testing User Context Management")
    print("=" * 50)
    
    # Create user context manager without cache (in-memory)
    context_mgr = UserContextManager(cache=None)
    user_id = 12345
    
    # Test data richness calculation
    nhtsa_data = create_sample_nhtsa_data()
    autodev_data = create_sample_autodev_data()
    
    nhtsa_richness = await context_mgr.calculate_data_richness(nhtsa_data)
    autodev_richness = await context_mgr.calculate_data_richness(autodev_data)
    
    print(f"NHTSA data richness: {nhtsa_richness:.2f}")
    print(f"Auto.dev data richness: {autodev_richness:.2f}")
    
    # Test level suggestions
    nhtsa_suggested = await context_mgr.suggest_optimal_level(user_id, nhtsa_richness)
    autodev_suggested = await context_mgr.suggest_optimal_level(user_id, autodev_richness)
    
    print(f"NHTSA suggested level: {nhtsa_suggested.name}")
    print(f"Auto.dev suggested level: {autodev_suggested.name}")
    
    # Test user tracking
    print("\nTracking user behavior...")
    await context_mgr.track_vin_search(user_id, "1HGBH41JXMN109186", InformationLevel.STANDARD, is_mobile=True)
    await context_mgr.track_level_change(user_id, InformationLevel.STANDARD, InformationLevel.DETAILED)
    await context_mgr.track_action(user_id, "share_vin")
    
    # Get updated context
    user_context = await context_mgr.get_user_context_dict(user_id)
    print(f"User context after tracking: {user_context}")


async def test_level_transitions():
    """Test level transition messages"""
    print("\n\n🔄 Testing Level Transitions")
    print("=" * 50)
    
    transitions = [
        (InformationLevel.ESSENTIAL, InformationLevel.STANDARD),
        (InformationLevel.STANDARD, InformationLevel.DETAILED),
        (InformationLevel.DETAILED, InformationLevel.COMPLETE),
        (InformationLevel.COMPLETE, InformationLevel.ESSENTIAL),
        (InformationLevel.DETAILED, InformationLevel.STANDARD)
    ]
    
    for from_level, to_level in transitions:
        message = create_level_transition_message(from_level, to_level)
        print(f"{from_level.name} → {to_level.name}:")
        print(f"  {message}")


async def test_data_analysis():
    """Test data analysis and suggestions"""
    print("\n\n📊 Testing Data Analysis")
    print("=" * 50)
    
    test_cases = [
        ("Minimal NHTSA", {"attributes": {"vin": "123", "year": "2020"}}),
        ("Rich NHTSA", create_sample_nhtsa_data()),
        ("Rich Auto.dev", create_sample_autodev_data()),
        ("Empty data", {"attributes": {}}),
    ]
    
    for name, data in test_cases:
        print(f"\n{name}:")
        print("-" * len(name))
        
        # Available levels
        available = get_available_disclosure_levels(data)
        print(f"Available levels: {[level.name for level in available]}")
        
        # Suggested level
        suggested = suggest_information_level(data)
        print(f"Suggested level: {suggested.name}")
        
        # Data richness (requires context manager)
        context_mgr = UserContextManager(cache=None)
        richness = await context_mgr.calculate_data_richness(data)
        print(f"Data richness: {richness:.2f}")


async def main():
    """Run all tests"""
    print("🚗 Smart Formatting System Test Suite")
    print("=" * 60)
    
    try:
        await test_progressive_disclosure()
        await test_mobile_vs_desktop()
        await test_keyboard_generation()
        await test_user_context()
        await test_level_transitions()
        await test_data_analysis()
        
        print("\n\n✅ All tests completed successfully!")
        print("\nKey Improvements Demonstrated:")
        print("• Progressive disclosure reduces information overload")
        print("• Mobile formatting optimizes for smaller screens")
        print("• Adaptive keyboards provide contextual options")
        print("• User learning improves experience over time")
        print("• Graceful fallbacks ensure reliability")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
