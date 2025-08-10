#!/usr/bin/env python3
"""
Test script to verify the settings keyboard layout changes
"""

import sys
import os

# Add the project root to the path so we can import vinbot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.keyboards import get_settings_keyboard


def test_settings_keyboard():
    print("Testing settings keyboard layout...")
    
    # Test with AutoDev service selected and no API keys
    print("1. Testing keyboard with AutoDev service and no API keys...")
    keyboard = get_settings_keyboard(current_service="AutoDev", has_carsxe_key=False, has_autodev_key=False)
    
    # Check that we have the expected number of rows
    assert len(keyboard.inline_keyboard) == 4, "Keyboard should have 4 rows"
    
    # Check the service selection row
    service_row = keyboard.inline_keyboard[0]
    assert len(service_row) == 2, "Service row should have 2 buttons"
    
    # Check the AutoDev button
    autodev_button = keyboard.inline_keyboard[1][0]
    assert "✅" in autodev_button.text, "AutoDev button should have checkmark"
    
    # Check that we always have the Auto.dev API key button
    api_key_button = keyboard.inline_keyboard[2][0]
    assert "Add Auto.dev API Key" in api_key_button.text, "Should always show Add Auto.dev API Key button"
    assert api_key_button.callback_data == "add_api_key:AutoDev", "Button should have correct callback data"
    
    print("   ✓ AutoDev service selected correctly")
    print("   ✓ Add Auto.dev API Key button is always visible")
    
    # Test with NHTSA service selected and Auto.dev API key set
    print("2. Testing keyboard with NHTSA service and Auto.dev API key set...")
    keyboard = get_settings_keyboard(current_service="NHTSA", has_carsxe_key=False, has_autodev_key=True)
    
    # Check that we have the expected number of rows
    assert len(keyboard.inline_keyboard) == 4, "Keyboard should have 4 rows"
    
    # Check the service selection row
    service_row = keyboard.inline_keyboard[0]
    assert len(service_row) == 2, "Service row should have 2 buttons"
    
    # Check the NHTSA button
    nhtsa_button = keyboard.inline_keyboard[0][1]
    assert "✅" in nhtsa_button.text, "NHTSA button should have checkmark"
    
    # Check that we still have the Auto.dev API key button
    api_key_button = keyboard.inline_keyboard[2][0]
    assert "Update Auto.dev API Key" in api_key_button.text, "Should show Update Auto.dev API Key button"
    assert api_key_button.callback_data == "update_api_key:AutoDev", "Button should have correct callback data"
    
    print("   ✓ NHTSA service selected correctly")
    print("   ✓ Update Auto.dev API Key button is visible even when NHTSA is selected")
    
    print("\nAll keyboard tests passed! Settings keyboard layout is working correctly.")


if __name__ == "__main__":
    test_settings_keyboard()