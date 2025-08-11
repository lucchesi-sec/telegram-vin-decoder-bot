#!/usr/bin/env python3
"""
Test script to compare formatting of Auto.dev and NHTSA data
"""

import sys
import os

# Add the project root to the path so we can import vinbot modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vinbot.formatter import format_vehicle_summary


def test_formatters():
    print("Testing formatters for Auto.dev and NHTSA data")
    print("=" * 50)
    
    # Sample Auto.dev data
    autodev_data = {
        "success": True,
        "vin": "1FTEW1E88HKE34785",
        "attributes": {
            "make": "Ford",
            "model": "F-150",
            "year": 2017,
            "engine": "3.5l V6",
            "cylinders": 6,
            "displacement": 3.5,
            "fuel_type": "flex-fuel (unleaded/E85)",
            "horsepower": 282,
            "torque": 253,
            "configuration": "V",
            "compressor_type": "NA",
            "transmission": "6A",
            "transmission_type": "AUTOMATIC",
            "number_of_speeds": "6",
            "automatic_type": "Shiftable automatic",
            "drive_type": "four wheel drive",
            "doors": "4",
            "body_type": "Truck",
            "vehicle_style": "Crew Cab Pickup",
            "vehicle_size": "Large",
            "epa_class": "Standard Pickup Trucks",
            "mpg_city": "17",
            "mpg_highway": "23",
            "trim": "XL",
            "features": [
                "Kicker Subwoofer",
                "Ford Telematics Powered By Telogis",
                "Full Coverage Rubber Floor Mats",
                "110v/400w Outlet",
                "Flex-Fuel Badge (Fleet)",
                "Plastic Drop-In Bedliner",
                "Manual-Folding, Dual Manual Glass Mirrors",
                "Spray-In Bedliner",
                "BoxLink",
                "Hard Tonneau Pickup Box Cover",
                "Front License Plate Bracket",
                "Rear Window Defroster",
                "Bed Divider",
                "Tailgate Step",
                "LED Side-Mirror Spotlights"
            ],
            "colors": [
                "Caribou Metallic",
                "Lightning Blue Metallic",
                "Race Red",
                "Oxford White",
                "Ingot Silver Metallic",
                "Magnetic Metallic",
                "Shadow Black",
                "Blue Jeans Metallic",
                "Lithium Gray"
            ]
        },
        "service": "AutoDev",
        "cached": False
    }
    
    # Sample NHTSA data
    nhtsa_data = {
        "success": True,
        "vin": "1HGBH41JXMN109186",
        "attributes": {
            "vin": "1HGBH41JXMN109186",
            "year": "1995",
            "make": "HONDA",
            "model": "ACCORD",
            "body": "SEDAN",
            "fuel_type": "GASOLINE",
            "gears": "MANUAL",
            "drive": "FWD",
            "manufacturer": "HONDA MANUFACTURING OF AMERICA INC",
            "plant_country": "UNITED STATES (USA)",
            "engine_manufacturer": "HONDA MANUFACTURING OF AMERICA INC",
            "length_mm": "4620",
            "width_mm": "1730",
            "height_mm": "1400",
            "wheelbase_mm": "2620",
            "weight_empty_kg": "1350",
            "max_speed_kmh": "180",
            "no_of_doors": "4",
            "no_of_seats": "5",
            "abs": "TRUE"
        },
        "service": "NHTSA",
        "cached": False
    }
    
    print("Auto.dev Data Formatting:")
    print("-" * 25)
    autodev_summary = format_vehicle_summary(autodev_data)
    print(autodev_summary)
    
    print("\n" + "=" * 50)
    
    print("NHTSA Data Formatting:")
    print("-" * 25)
    nhtsa_summary = format_vehicle_summary(nhtsa_data)
    print(nhtsa_summary)


if __name__ == "__main__":
    test_formatters()