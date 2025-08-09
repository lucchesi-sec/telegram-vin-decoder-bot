from typing import Any, Dict, List


def _format_value(value: Any) -> str:
    """Format a value for display, handling None and empty strings"""
    if value is None or value == "":
        return "N/A"
    return str(value).strip()


def format_vehicle_summary(data: Dict[str, Any]) -> str:
    """Format complete vehicle information from CarsXE API response"""
    
    # Handle both direct attributes and nested attributes structure
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}
    
    if not attrs:
        return "Could not parse vehicle data from response."
    
    lines: List[str] = []
    
    # VIN and Basic Info
    lines.append("🚗 **VEHICLE INFORMATION**")
    lines.append("=" * 30)
    
    # Primary vehicle details
    vin = attrs.get("vin")
    if vin:
        lines.append(f"**VIN:** `{vin}`")
    
    year = attrs.get("year")
    make = attrs.get("make")
    model = attrs.get("model")
    if year or make or model:
        vehicle_desc = " ".join(str(v) for v in [year, make, model] if v)
        lines.append(f"**Vehicle:** {vehicle_desc}")
    
    # Basic specifications
    lines.append("\n📋 **BASIC SPECS**")
    lines.append("-" * 20)
    
    basic_fields = [
        ("Product Type", attrs.get("product_type")),
        ("Body Style", attrs.get("body")),
        ("Series", attrs.get("series")),
        ("Trim", attrs.get("trim")),
        ("Fuel Type", attrs.get("fuel_type")),
        ("Transmission", attrs.get("gears")),
        ("Drive Type", attrs.get("drive")),
        ("Emission Standard", attrs.get("emission_standard")),
    ]
    
    for label, value in basic_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)}")
    
    # Manufacturing Info
    lines.append("\n🏭 **MANUFACTURING**")
    lines.append("-" * 20)
    
    manufacturing_fields = [
        ("Manufacturer", attrs.get("manufacturer")),
        ("Plant Address", attrs.get("manufacturer_address")),
        ("Plant Country", attrs.get("plant_country")),
        ("Engine Manufacturer", attrs.get("engine_manufacturer")),
    ]
    
    for label, value in manufacturing_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)}")
    
    # Dimensions
    lines.append("\n📏 **DIMENSIONS**")
    lines.append("-" * 20)
    
    dimension_fields = [
        ("Length", attrs.get("length_mm"), "mm"),
        ("Width", attrs.get("width_mm"), "mm"),
        ("Height", attrs.get("height_mm"), "mm"),
        ("Wheelbase", attrs.get("wheelbase_mm"), "mm"),
        ("Track Front", attrs.get("track_front_mm"), "mm"),
        ("Track Rear", attrs.get("track_rear_mm"), "mm"),
    ]
    
    for label, value, unit in dimension_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)} {unit}")
    
    # Weight and Capacity
    lines.append("\n⚖️ **WEIGHT & CAPACITY**")
    lines.append("-" * 20)
    
    weight_fields = [
        ("Empty Weight", attrs.get("weight_empty_kg"), "kg"),
        ("Max Weight", attrs.get("max_weight_kg"), "kg"),
        ("Max Roof Load", attrs.get("max_roof_load_kg"), "kg"),
        ("Max Trailer Load (w/o brakes)", attrs.get("permitted_trailer_load_without_brakes_kg"), "kg"),
        ("Min Trunk Capacity", attrs.get("min_trunk_capacity_liters"), "L"),
        ("Max Trunk Capacity", attrs.get("max_trunk_capacity_liters"), "L"),
    ]
    
    for label, value, unit in weight_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)} {unit}")
    
    # Performance
    lines.append("\n🏁 **PERFORMANCE**")
    lines.append("-" * 20)
    
    performance_fields = [
        ("Max Speed", attrs.get("max_speed_kmh"), "km/h"),
        ("CO2 Emission", attrs.get("avg_co2_emission_g_km"), "g/km"),
    ]
    
    for label, value, unit in performance_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)} {unit}")
    
    # Features
    lines.append("\n🔧 **FEATURES**")
    lines.append("-" * 20)
    
    feature_fields = [
        ("Number of Doors", attrs.get("no_of_doors")),
        ("Number of Seats", attrs.get("no_of_seats")),
        ("Number of Axles", attrs.get("no_of_axels")),
        ("Steering Type", attrs.get("steering_type")),
        ("Front Suspension", attrs.get("front_suspension")),
        ("Rear Suspension", attrs.get("rear_suspension")),
        ("Rear Brakes", attrs.get("rear_brakes")),
        ("ABS", attrs.get("abs")),
        ("Wheel Size", attrs.get("wheel_size")),
    ]
    
    for label, value in feature_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)}")
    
    # VIN Details
    lines.append("\n🔍 **VIN DETAILS**")
    lines.append("-" * 20)
    
    vin_fields = [
        ("Check Digit", attrs.get("check_digit")),
        ("Sequential Number", attrs.get("sequential_number")),
    ]
    
    for label, value in vin_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)}")
    
    # Add any additional fields that weren't covered
    covered_keys = {
        "vin", "year", "make", "model", "product_type", "body", "series", "trim",
        "fuel_type", "gears", "drive", "emission_standard", "manufacturer",
        "manufacturer_address", "plant_country", "engine_manufacturer",
        "length_mm", "width_mm", "height_mm", "wheelbase_mm", "track_front_mm",
        "track_rear_mm", "weight_empty_kg", "max_weight_kg", "max_roof_load_kg",
        "permitted_trailer_load_without_brakes_kg", "min_trunk_capacity_liters",
        "max_trunk_capacity_liters", "max_speed_kmh", "avg_co2_emission_g_km",
        "no_of_doors", "no_of_seats", "no_of_axels", "steering_type",
        "front_suspension", "rear_suspension", "rear_brakes", "abs", "wheel_size",
        "check_digit", "sequential_number", "wheel_size_array", "wheelbase_array_mm"
    }
    
    # Check for any uncovered fields with values
    other_fields = []
    for key, value in attrs.items():
        if key not in covered_keys and value and value != "":
            other_fields.append((key.replace("_", " ").title(), value))
    
    if other_fields:
        lines.append("\n📌 **OTHER INFORMATION**")
        lines.append("-" * 20)
        for label, value in other_fields:
            lines.append(f"**{label}:** {_format_value(value)}")
    
    return "\n".join(lines)

