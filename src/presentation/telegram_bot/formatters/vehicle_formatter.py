"""Vehicle data formatters for Telegram messages."""

from typing import Dict, Any
from src.presentation.telegram_bot.formatters.premium_features_formatter import PremiumFeaturesFormatter


class VehicleFormatter:
    """Formatter for vehicle data in Telegram messages."""
    
    @staticmethod
    def format_summary(data: Dict[str, Any]) -> str:
        """Format vehicle information for Telegram message."""
        return format_vehicle_summary(data)
    
    @staticmethod
    def format_detailed(data: Dict[str, Any]) -> str:
        """Format detailed vehicle information for Telegram message."""
        # For now, use the same format as summary
        return format_vehicle_summary(data)


def format_vehicle_summary(data: Dict[str, Any]) -> str:
    """Format vehicle information for Telegram message.
    
    Args:
        data: Vehicle data from decoder
        
    Returns:
        Formatted message text
    """
    # Handle both direct attributes and nested attributes structure
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}
    
    if not attrs:
        return "Could not parse vehicle data from response."
    
    lines = []
    
    # Vehicle header
    year = attrs.get("year", "")
    make = attrs.get("make", "")
    model = attrs.get("model", "")
    
    vehicle_desc = " ".join(str(v) for v in [year, make, model] if v)
    if vehicle_desc:
        lines.append(f"🚗 *{vehicle_desc}*")
    else:
        lines.append("🚗 *Vehicle Information*")
    
    # Add premium badge if applicable
    premium_summary, feature_count = PremiumFeaturesFormatter.format_premium_summary(data)
    premium_badge = PremiumFeaturesFormatter.format_premium_badge(feature_count)
    if premium_badge:
        lines.append(premium_badge)
    
    lines.append("━" * 25)
    
    # Key specs with premium summary
    specs = []
    body = attrs.get("body_type") or attrs.get("body", "")
    fuel = attrs.get("fuel_type", "")
    drive = attrs.get("drive_type") or attrs.get("drive", "")
    
    if body:
        specs.append(body)
    if fuel:
        specs.append(fuel)
    if drive:
        specs.append(drive)
    
    if specs:
        lines.append(f"📌 {' • '.join(specs)}")
    
    # Add premium features summary if available
    if premium_summary:
        lines.append(f"✨ {premium_summary}")
    
    # VIN
    vin = attrs.get("vin", "")
    if vin:
        lines.append(f"\n`{vin}`")
    
    # Basic information
    basic_fields = [
        ("Engine", attrs.get("engine")),
        ("Transmission", attrs.get("transmission")),
        ("Cylinders", attrs.get("cylinders")),
        ("Doors", attrs.get("doors")),
    ]
    
    has_basic_info = False
    for label, value in basic_fields:
        if value:
            if not has_basic_info:
                lines.append("\n📋 *SPECIFICATIONS*")
                lines.append("─" * 20)
                has_basic_info = True
            lines.append(f"*{label}:* {value}")
    
    # Add premium features section
    features_section = PremiumFeaturesFormatter.format_features_section(
        PremiumFeaturesFormatter.extract_features(data)
    )
    if features_section:
        lines.append(features_section)
    
    return "\n".join(lines)


def format_error_message(error: str) -> str:
    """Format error message for Telegram.
    
    Args:
        error: Error message
        
    Returns:
        Formatted error message
    """
    return f"❌ *Error*\n\n{error}"