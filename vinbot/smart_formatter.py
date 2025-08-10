"""
Smart Formatter with Progressive Disclosure and Mobile Optimization

This module provides intelligent formatting for VIN decode responses with:
- Progressive disclosure (Essential -> Standard -> Detailed -> Complete)
- Mobile-first responsive layouts
- Context-aware information presentation
- Enhanced visual hierarchy and readability
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class InformationLevel(Enum):
    """Information disclosure levels for progressive enhancement"""
    ESSENTIAL = 1    # Essential info only (5-8 lines): Year, Make, Model, Body, Fuel
    STANDARD = 2     # Standard info (15-20 lines): + Engine, Transmission, Key Features  
    DETAILED = 3     # Detailed info (30-40 lines): + Dimensions, Performance, Manufacturing
    COMPLETE = 4     # Complete info (current behavior): Everything available


class DisplayMode(Enum):
    """Display modes for different user contexts"""
    MOBILE = "mobile"      # Optimized for mobile screens (35-40 char width)
    DESKTOP = "desktop"    # Optimized for desktop/web clients (60+ char width)
    AUTO = "auto"          # Auto-detect based on context


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


def _extract_vehicle_attributes(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and normalize vehicle attributes from API response"""
    # Handle both direct attributes and nested attributes structure
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}
    
    # Determine service type for conditional formatting
    is_autodev = data.get("service") == "AutoDev"
    
    return {
        "attrs": attrs,
        "is_autodev": is_autodev,
        "has_history": "history" in data and data["history"],
        "has_marketvalue": "marketvalue" in data and data["marketvalue"],
        "from_cache": data.get("from_cache", False)
    }


def format_vehicle_smart_card(
    data: Dict[str, Any], 
    level: InformationLevel = InformationLevel.STANDARD,
    mode: DisplayMode = DisplayMode.MOBILE
) -> str:
    """
    Format vehicle information with smart progressive disclosure
    
    Args:
        data: Vehicle data from API response
        level: Information disclosure level
        mode: Display mode (mobile/desktop/auto)
        
    Returns:
        Formatted string optimized for the specified level and mode
    """
    extracted = _extract_vehicle_attributes(data)
    attrs = extracted["attrs"]
    is_autodev = extracted["is_autodev"]
    
    if not attrs:
        return "❌ **Unable to parse vehicle data**\n\nPlease try again or contact support."
    
    # Route to appropriate formatter based on level
    if level == InformationLevel.ESSENTIAL:
        return _format_essential_info(attrs, is_autodev, mode)
    elif level == InformationLevel.STANDARD:
        return _format_standard_info(attrs, is_autodev, mode, extracted)
    elif level == InformationLevel.DETAILED:
        return _format_detailed_info(attrs, is_autodev, mode, extracted)
    else:  # COMPLETE
        return _format_complete_info(attrs, is_autodev, mode, extracted)


def _format_essential_info(
    attrs: Dict[str, Any], 
    is_autodev: bool, 
    mode: DisplayMode
) -> str:
    """Format essential vehicle information only (5-8 lines)"""
    lines = []
    
    # Vehicle header with icon
    year = attrs.get("year", "")
    make = attrs.get("make", "")
    model = attrs.get("model", "")
    trim = attrs.get("trim", "")
    
    # Get body type for icon
    body = attrs.get("body_type" if is_autodev else "body", "")
    icon = _get_vehicle_icon(body)
    
    # Create vehicle title
    vehicle_parts = [str(v) for v in [year, make, model, trim] if v]
    vehicle_title = " ".join(vehicle_parts) if vehicle_parts else "Vehicle Information"
    
    lines.append(f"{icon} **{vehicle_title}**")
    
    # Mobile vs Desktop separator
    if mode == DisplayMode.MOBILE:
        lines.append("━" * min(len(vehicle_title) + 2, 35))
    else:
        lines.append("━" * min(len(vehicle_title) + 2, 50))
    
    # Essential specs in compact format
    specs = []
    if body:
        specs.append(body)
    
    fuel = attrs.get("fuel_type", "")
    if fuel:
        specs.append(fuel)
    
    drive = attrs.get("drive_type" if is_autodev else "drive", "")
    if drive:
        specs.append(drive)
    
    if specs:
        if mode == DisplayMode.MOBILE:
            # Stack specs vertically for mobile
            lines.append("🔹 **Quick Facts**")
            for spec in specs[:3]:  # Limit to 3 for mobile
                lines.append(f"• {spec}")
        else:
            # Horizontal layout for desktop
            lines.append(f"🔹 **Quick Facts:** {' • '.join(specs)}")
    
    # VIN at bottom
    vin = attrs.get("vin", "")
    if vin:
        lines.append(f"\n`{vin}`")
    
    return "\n".join(lines)


def _format_standard_info(
    attrs: Dict[str, Any], 
    is_autodev: bool, 
    mode: DisplayMode,
    extracted: Dict[str, Any]
) -> str:
    """Format standard vehicle information (15-20 lines)"""
    lines = []
    
    # Start with essential info
    essential = _format_essential_info(attrs, is_autodev, mode)
    lines.extend(essential.split('\n')[:-1])  # Remove VIN for now
    
    # Add engine and performance info
    lines.append("\n⚙️ **Engine & Power**")
    
    if is_autodev:
        engine = attrs.get("engine", "")
        hp = attrs.get("horsepower", "")
        transmission = attrs.get("transmission", "")
        mpg_city = attrs.get("mpg_city", "")
        mpg_highway = attrs.get("mpg_highway", "")
        
        if engine:
            engine_line = f"• {engine}"
            if hp:
                engine_line += f" • {hp} HP"
            lines.append(engine_line)
        
        if transmission:
            lines.append(f"• {transmission}")
        
        if mpg_city and mpg_highway:
            lines.append(f"• {mpg_city} City / {mpg_highway} Highway MPG")
    else:
        # NHTSA formatting
        fuel_type = attrs.get("fuel_type", "")
        gears = attrs.get("gears", "")
        max_speed = attrs.get("max_speed_kmh", "")
        
        if fuel_type:
            lines.append(f"• Fuel: {fuel_type}")
        if gears:
            lines.append(f"• Transmission: {gears}")
        if max_speed:
            lines.append(f"• Max Speed: {max_speed} km/h")
    
    # Add basic features
    lines.append("\n📋 **Key Features**")
    
    doors = attrs.get("doors" if is_autodev else "no_of_doors", "")
    seats = attrs.get("standard_seating" if is_autodev else "no_of_seats", "")
    
    features = []
    if doors:
        features.append(f"{doors} Doors")
    if seats:
        features.append(f"{seats} Seats")
    
    if is_autodev:
        vehicle_size = attrs.get("vehicle_size", "")
        if vehicle_size:
            features.append(vehicle_size)
    else:
        abs_system = attrs.get("abs", "")
        if abs_system:
            features.append(f"ABS: {abs_system}")
    
    if features:
        if mode == DisplayMode.MOBILE:
            for feature in features:
                lines.append(f"• {feature}")
        else:
            lines.append(f"• {' • '.join(features)}")
    else:
        lines.append("• Information not available")
    
    # Add cache indicator if from cache
    if extracted.get("from_cache"):
        lines.append("\n⚡ _Retrieved from cache_")
    
    # VIN at bottom
    vin = attrs.get("vin", "")
    if vin:
        lines.append(f"\n`{vin}`")
    
    return "\n".join(lines)


def _format_detailed_info(
    attrs: Dict[str, Any], 
    is_autodev: bool, 
    mode: DisplayMode,
    extracted: Dict[str, Any]
) -> str:
    """Format detailed vehicle information (30-40 lines)"""
    lines = []
    
    # Start with standard info
    standard = _format_standard_info(attrs, is_autodev, mode, extracted)
    lines.extend(standard.split('\n')[:-1])  # Remove VIN for now
    
    # Add manufacturing information
    if not is_autodev:  # NHTSA has manufacturing data
        lines.append("\n🏭 **Manufacturing**")
        
        manufacturer = attrs.get("manufacturer", "")
        country = attrs.get("plant_country", "")
        
        mfg_info = []
        if manufacturer:
            mfg_info.append(manufacturer)
        if country:
            mfg_info.append(f"Made in {country}")
        
        if mfg_info:
            if mode == DisplayMode.MOBILE:
                for info in mfg_info:
                    lines.append(f"• {info}")
            else:
                lines.append(f"• {' • '.join(mfg_info)}")
        else:
            lines.append("• Information not available")
    
    # Add dimensions (NHTSA only)
    if not is_autodev:
        lines.append("\n📏 **Dimensions**")
        
        length = attrs.get("length_mm", "")
        width = attrs.get("width_mm", "")
        height = attrs.get("height_mm", "")
        wheelbase = attrs.get("wheelbase_mm", "")
        
        dimensions = []
        if length:
            dimensions.append(f"L: {length}mm")
        if width:
            dimensions.append(f"W: {width}mm")
        if height:
            dimensions.append(f"H: {height}mm")
        if wheelbase:
            dimensions.append(f"WB: {wheelbase}mm")
        
        if dimensions:
            if mode == DisplayMode.MOBILE:
                # Group dimensions in pairs for mobile
                for i in range(0, len(dimensions), 2):
                    pair = dimensions[i:i+2]
                    lines.append(f"• {' • '.join(pair)}")
            else:
                lines.append(f"• {' • '.join(dimensions)}")
        else:
            lines.append("• Dimension data not available")
    
    # Add Auto.dev specific features
    if is_autodev:
        features = attrs.get("features", [])
        if features:
            lines.append("\n✨ **Vehicle Features**")
            # Show all features with organized display
            for i, feature in enumerate(features, 1):
                lines.append(f"• {feature}")
                
                # Add spacing every 8 items for better readability on mobile
                if mode == DisplayMode.MOBILE and i % 8 == 0 and i < len(features):
                    lines.append("")  # Add empty line for visual separation
                # Add spacing every 10 items for desktop
                elif mode != DisplayMode.MOBILE and i % 10 == 0 and i < len(features):
                    lines.append("")  # Add empty line for visual separation
    
    # Add performance data
    lines.append("\n🏁 **Performance**")
    
    if is_autodev:
        # Auto.dev performance metrics
        hp = attrs.get("horsepower", "")
        torque = attrs.get("torque", "")
        cylinders = attrs.get("cylinders", "")
        
        perf_data = []
        if hp:
            perf_data.append(f"{hp} HP")
        if torque:
            perf_data.append(f"{torque} lb-ft")
        if cylinders:
            perf_data.append(f"{cylinders} Cylinders")
        
        if perf_data:
            lines.append(f"• {' • '.join(perf_data)}")
        else:
            lines.append("• Performance data not available")
    else:
        # NHTSA performance metrics
        max_speed = attrs.get("max_speed_kmh", "")
        co2 = attrs.get("avg_co2_emission_g_km", "")
        weight = attrs.get("weight_empty_kg", "")
        
        perf_data = []
        if max_speed:
            perf_data.append(f"Max: {max_speed} km/h")
        if co2:
            perf_data.append(f"CO2: {co2} g/km")
        if weight:
            perf_data.append(f"Weight: {weight} kg")
        
        if perf_data:
            lines.append(f"• {' • '.join(perf_data)}")
        else:
            lines.append("• Performance data not available")
    
    # Add cache indicator if from cache
    if extracted.get("from_cache"):
        lines.append("\n⚡ _Retrieved from cache_")
    
    # VIN at bottom
    vin = attrs.get("vin", "")
    if vin:
        lines.append(f"\n`{vin}`")
    
    return "\n".join(lines)


def _format_complete_info(
    attrs: Dict[str, Any], 
    is_autodev: bool, 
    mode: DisplayMode,
    extracted: Dict[str, Any]
) -> str:
    """Format complete vehicle information (full data)"""
    # For complete info, fall back to the original comprehensive formatter
    # but with improved mobile formatting
    from .formatter import format_vehicle_summary
    
    # Reconstruct the data structure expected by the original formatter
    data = {
        "attributes": attrs,
        "service": "AutoDev" if is_autodev else "NHTSA"
    }
    
    if extracted.get("has_history"):
        data["history"] = True
    if extracted.get("has_marketvalue"):
        data["marketvalue"] = True
    if extracted.get("from_cache"):
        data["from_cache"] = True
    
    return format_vehicle_summary(data)


def get_available_disclosure_levels(data: Dict[str, Any]) -> List[InformationLevel]:
    """
    Determine which information levels are available for the given data
    
    Args:
        data: Vehicle data from API response
        
    Returns:
        List of available information levels
    """
    extracted = _extract_vehicle_attributes(data)
    attrs = extracted["attrs"]
    
    levels = [InformationLevel.ESSENTIAL]  # Always available
    
    # Check if we have enough data for standard level
    basic_fields = ["year", "make", "model"]
    if any(attrs.get(field) for field in basic_fields):
        levels.append(InformationLevel.STANDARD)
    
    # Check if we have enough data for detailed level
    detailed_fields = ["manufacturer", "length_mm", "horsepower", "features"]
    if any(attrs.get(field) for field in detailed_fields):
        levels.append(InformationLevel.DETAILED)
    
    # Complete is always available if we have any data
    if attrs:
        levels.append(InformationLevel.COMPLETE)
    
    return levels


def suggest_information_level(data: Dict[str, Any], user_context: Optional[Dict] = None) -> InformationLevel:
    """
    Suggest the optimal information level based on data richness and user context
    
    Args:
        data: Vehicle data from API response
        user_context: Optional user context (history, preferences, etc.)
        
    Returns:
        Suggested information level
    """
    extracted = _extract_vehicle_attributes(data)
    attrs = extracted["attrs"]
    is_autodev = extracted["is_autodev"]
    
    # Default to standard for most users
    suggested = InformationLevel.STANDARD
    
    # If it's Auto.dev data with rich features, suggest detailed
    if is_autodev and attrs.get("features") and len(attrs.get("features", [])) > 10:
        suggested = InformationLevel.DETAILED
    
    # If user has shown preference for detailed data (from context)
    if user_context and user_context.get("prefers_detailed", False):
        suggested = InformationLevel.DETAILED
    
    # If user is on mobile (from context), stick to standard or essential
    if user_context and user_context.get("is_mobile", False):
        suggested = InformationLevel.STANDARD
    
    # If data is very limited, use essential
    basic_fields = ["year", "make", "model"]
    if sum(1 for field in basic_fields if attrs.get(field)) < 2:
        suggested = InformationLevel.ESSENTIAL
    
    return suggested


def format_level_preview(level: InformationLevel) -> str:
    """Get a user-friendly description of what each level contains"""
    descriptions = {
        InformationLevel.ESSENTIAL: "🔹 **Quick Facts** - Year, Make, Model, Body Type",
        InformationLevel.STANDARD: "📋 **Standard Info** - + Engine, Performance, Key Features", 
        InformationLevel.DETAILED: "📊 **Detailed View** - + Dimensions, Manufacturing, Full Specs",
        InformationLevel.COMPLETE: "📚 **Everything** - Complete technical data and all sections"
    }
    return descriptions.get(level, "Unknown level")
