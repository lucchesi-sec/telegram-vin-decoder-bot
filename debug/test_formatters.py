#!/usr/bin/env python3
"""
Test the formatters with sample data
"""

import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.formatter import format_vehicle_summary
from vinbot.formatter_extensions import format_market_value, format_history

# Load the sample data we captured earlier
print("Loading sample data...")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Load specs data
with open(os.path.join(DATA_DIR, "specs_response.json"), "r") as f:
    specs_data = json.load(f)

# Load market value data
with open(os.path.join(DATA_DIR, "marketvalue_response.json"), "r") as f:
    marketvalue_data = json.load(f)

# Load history data
with open(os.path.join(DATA_DIR, "history_response.json"), "r") as f:
    history_data = json.load(f)

# Combine into a single data object like the new client would return
combined_data = specs_data.copy()
combined_data["marketvalue"] = marketvalue_data
combined_data["history"] = history_data

print("=" * 60)
print("TESTING FORMATTERS WITH SAMPLE DATA")
print("=" * 60)

# Test main summary formatter
print("\n1. MAIN VEHICLE SUMMARY")
print("-" * 40)
summary = format_vehicle_summary(combined_data)
print(summary)

# Test market value formatter
print("\n" + "=" * 60)
print("2. MARKET VALUE INFORMATION")
print("-" * 40)
market = format_market_value(combined_data)
print(market)

# Test history formatter
print("\n" + "=" * 60)
print("3. VEHICLE HISTORY")
print("-" * 40)
history = format_history(combined_data)
print(history)

print("\n" + "=" * 60)
print("✅ All formatters tested successfully!")