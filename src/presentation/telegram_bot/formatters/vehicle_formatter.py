"""Vehicle data formatters for Telegram messages."""

from typing import Dict, Any
from telegram.constants import ParseMode


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
    
    lines.append("━" * 25)
    
    # Key specs
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
    
    return "\n".join(lines)


def format_error_message(error: str) -> str:
    """Format error message for Telegram.
    
    Args:
        error: Error message
        
    Returns:
        Formatted error message
    """
    return f"❌ *Error*\n\n{error}"