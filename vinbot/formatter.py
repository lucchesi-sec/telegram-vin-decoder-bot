from typing import Any, Dict, List, Optional


def _format_value(value: Any) -> str:
    """Format a value for display, handling None and empty strings"""
    if value is None or value == "":
        return "N/A"
    return str(value).strip()


def _get_vehicle_icon(body_type: str) -> str:
    """Get appropriate emoji icon based on vehicle body type"""
    if not body_type:
        return "🚗"
    
    body_lower = body_type.lower()
    if "truck" in body_lower or "pickup" in body_lower:
        return "🚚"
    elif "suv" in body_lower or "sport utility" in body_lower:
        return "🚙"
    elif "van" in body_lower or "minivan" in body_lower:
        return "🚐"
    elif "motorcycle" in body_lower:
        return "🏍️"
    elif "bus" in body_lower:
        return "🚌"
    elif "convertible" in body_lower or "roadster" in body_lower:
        return "🏎️"
    elif "coupe" in body_lower:
        return "🚗"
    elif "sedan" in body_lower:
        return "🚗"
    elif "wagon" in body_lower:
        return "🚙"
    else:
        return "🚗"


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


def format_vehicle_card(data: Dict[str, Any], from_cache: bool = False) -> str:
    """Format a concise vehicle card summary - the initial view users see"""
    
    # Handle both direct attributes and nested attributes structure
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}
    
    if not attrs:
        return "Could not parse vehicle data from response."
    
    # Get basic info
    vin = attrs.get("vin", "Unknown")
    year = attrs.get("year", "")
    make = attrs.get("make", "")
    model = attrs.get("model", "")
    body = attrs.get("body", "")
    fuel = attrs.get("fuel_type", "")
    drive = attrs.get("drive", "")
    
    # Get vehicle icon
    icon = _get_vehicle_icon(body)
    
    # Build the card
    lines = []
    
    # Header with vehicle description
    vehicle_desc = " ".join(str(v) for v in [year, make, model] if v)
    if vehicle_desc:
        lines.append(f"{icon} **{vehicle_desc}**")
    else:
        lines.append(f"{icon} **Vehicle Information**")
    
    lines.append("━" * 25)
    
    # Key specs in compact format
    specs = []
    if body:
        specs.append(body)
    if fuel:
        specs.append(fuel)
    if drive:
        specs.append(drive)
    
    if specs:
        lines.append(f"📌 {' • '.join(specs)}")
    
    # Manufacturing info
    manufacturer = attrs.get("manufacturer", "")
    country = attrs.get("plant_country", "")
    if manufacturer or country:
        mfg_info = []
        if manufacturer:
            mfg_info.append(manufacturer)
        if country:
            mfg_info.append(f"Made in {country}")
        lines.append(f"🏭 {' • '.join(mfg_info)}")
    
    # Transmission info
    gears = attrs.get("gears", "")
    if gears:
        lines.append(f"⚙️ {gears}")
    
    # Most commonly requested specs in a consolidated view
    lines.append("\n📋 **SPECIFICATIONS**")
    lines.append("─" * 20)
    
    specs_fields = [
        ("Trim", attrs.get("trim")),
        ("Series", attrs.get("series")),
        ("Product Type", attrs.get("product_type")),
    ]
    
    for label, value in specs_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)}")
    
    # Dimensions
    lines.append("\n📏 **DIMENSIONS**")
    lines.append("─" * 20)
    
    dimension_fields = [
        ("Length", attrs.get("length_mm"), "mm"),
        ("Width", attrs.get("width_mm"), "mm"),
        ("Height", attrs.get("height_mm"), "mm"),
        ("Wheelbase", attrs.get("wheelbase_mm"), "mm"),
    ]
    
    for label, value, unit in dimension_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)} {unit}")
    
    # Weight
    weight_empty = attrs.get("weight_empty_kg")
    if weight_empty:
        lines.append(f"**Empty Weight:** {_format_value(weight_empty)} kg")
    
    # Performance
    lines.append("\n🏁 **PERFORMANCE**")
    lines.append("─" * 20)
    
    performance_fields = [
        ("Max Speed", attrs.get("max_speed_kmh"), "km/h"),
        ("CO2 Emission", attrs.get("avg_co2_emission_g_km"), "g/km"),
    ]
    
    for label, value, unit in performance_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)} {unit}")
    
    # Features
    lines.append("\n🔧 **FEATURES**")
    lines.append("─" * 20)
    
    feature_fields = [
        ("Doors", attrs.get("no_of_doors")),
        ("Seats", attrs.get("no_of_seats")),
        ("ABS", attrs.get("abs")),
    ]
    
    for label, value in feature_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)}")
    
    # Cache indicator
    if from_cache:
        lines.append("\n⚡ _Retrieved from cache_")
    
    # VIN at the bottom
    lines.append(f"\n`{vin}`")
    
    return "\n".join(lines)


def format_specs_section(data: Dict[str, Any]) -> str:
    """Format the basic specifications section"""
    
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}
    
    lines = ["📋 **SPECIFICATIONS**", "─" * 20]
    
    specs_fields = [
        ("Product Type", attrs.get("product_type")),
        ("Body Style", attrs.get("body")),
        ("Series", attrs.get("series")),
        ("Trim", attrs.get("trim")),
        ("Fuel Type", attrs.get("fuel_type")),
        ("Transmission", attrs.get("gears")),
        ("Drive Type", attrs.get("drive")),
        ("Emission Standard", attrs.get("emission_standard")),
    ]
    
    has_content = False
    for label, value in specs_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)}")
            has_content = True
    
    if not has_content:
        lines.append("_No specification data available_")
    
    return "\n".join(lines)


def format_manufacturing_section(data: Dict[str, Any]) -> str:
    """Format the manufacturing information section"""
    
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}
    
    lines = ["🏭 **MANUFACTURING**", "─" * 20]
    
    mfg_fields = [
        ("Manufacturer", attrs.get("manufacturer")),
        ("Plant Address", attrs.get("manufacturer_address")),
        ("Plant Country", attrs.get("plant_country")),
        ("Engine Manufacturer", attrs.get("engine_manufacturer")),
    ]
    
    has_content = False
    for label, value in mfg_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)}")
            has_content = True
    
    if not has_content:
        lines.append("_No manufacturing data available_")
    
    return "\n".join(lines)


def format_dimensions_section(data: Dict[str, Any]) -> str:
    """Format the dimensions section"""
    
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}
    
    lines = ["📏 **DIMENSIONS**", "─" * 20]
    
    dimension_fields = [
        ("Length", attrs.get("length_mm"), "mm"),
        ("Width", attrs.get("width_mm"), "mm"),
        ("Height", attrs.get("height_mm"), "mm"),
        ("Wheelbase", attrs.get("wheelbase_mm"), "mm"),
        ("Track Front", attrs.get("track_front_mm"), "mm"),
        ("Track Rear", attrs.get("track_rear_mm"), "mm"),
    ]
    
    has_content = False
    for label, value, unit in dimension_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)} {unit}")
            has_content = True
    
    # Weight info
    weight_fields = [
        ("Empty Weight", attrs.get("weight_empty_kg"), "kg"),
        ("Max Weight", attrs.get("max_weight_kg"), "kg"),
    ]
    
    for label, value, unit in weight_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)} {unit}")
            has_content = True
    
    if not has_content:
        lines.append("_No dimension data available_")
    
    return "\n".join(lines)


def format_performance_section(data: Dict[str, Any]) -> str:
    """Format the performance section"""
    
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}
    
    lines = ["🏁 **PERFORMANCE**", "─" * 20]
    
    performance_fields = [
        ("Max Speed", attrs.get("max_speed_kmh"), "km/h"),
        ("CO2 Emission", attrs.get("avg_co2_emission_g_km"), "g/km"),
    ]
    
    has_content = False
    for label, value, unit in performance_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)} {unit}")
            has_content = True
    
    # Add capacity info here too
    capacity_fields = [
        ("Max Roof Load", attrs.get("max_roof_load_kg"), "kg"),
        ("Max Trailer Load", attrs.get("permitted_trailer_load_without_brakes_kg"), "kg"),
        ("Min Trunk Capacity", attrs.get("min_trunk_capacity_liters"), "L"),
        ("Max Trunk Capacity", attrs.get("max_trunk_capacity_liters"), "L"),
    ]
    
    for label, value, unit in capacity_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)} {unit}")
            has_content = True
    
    if not has_content:
        lines.append("_No performance data available_")
    
    return "\n".join(lines)


def format_features_section(data: Dict[str, Any]) -> str:
    """Format the features section"""
    
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}
    
    lines = ["🔧 **FEATURES**", "─" * 20]
    
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
    
    has_content = False
    for label, value in feature_fields:
        if value:
            lines.append(f"**{label}:** {_format_value(value)}")
            has_content = True
    
    if not has_content:
        lines.append("_No feature data available_")
    
    return "\n".join(lines)


def format_comparison(data1: Dict[str, Any], data2: Dict[str, Any]) -> str:
    """Format a side-by-side comparison of two vehicles"""
    
    # Extract attributes
    attrs1 = data1.get("attributes", {}) if isinstance(data1, dict) else {}
    attrs2 = data2.get("attributes", {}) if isinstance(data2, dict) else {}
    
    # Get vehicle descriptions
    vehicle1 = " ".join(str(v) for v in [attrs1.get("year"), attrs1.get("make"), attrs1.get("model")] if v)
    vehicle2 = " ".join(str(v) for v in [attrs2.get("year"), attrs2.get("make"), attrs2.get("model")] if v)
    
    lines = ["📊 **VEHICLE COMPARISON**", "═" * 30]
    lines.append(f"**Vehicle 1:** {vehicle1 or 'Unknown'}")
    lines.append(f"**Vehicle 2:** {vehicle2 or 'Unknown'}")
    lines.append("─" * 30)
    
    # Compare key fields
    comparison_fields = [
        ("Body Style", "body"),
        ("Fuel Type", "fuel_type"),
        ("Transmission", "gears"),
        ("Drive Type", "drive"),
        ("Doors", "no_of_doors"),
        ("Seats", "no_of_seats"),
        ("Length (mm)", "length_mm"),
        ("Width (mm)", "width_mm"),
        ("Weight (kg)", "weight_empty_kg"),
        ("Max Speed (km/h)", "max_speed_kmh"),
    ]
    
    for label, field in comparison_fields:
        val1 = attrs1.get(field, "N/A")
        val2 = attrs2.get(field, "N/A")
        
        # Highlight differences
        if val1 != val2:
            lines.append(f"**{label}:**")
            lines.append(f"  • Vehicle 1: {_format_value(val1)}")
            lines.append(f"  • Vehicle 2: {_format_value(val2)} ⚠️")
        else:
            lines.append(f"**{label}:** {_format_value(val1)} ✓")
    
    return "\n".join(lines)

