"""Message adapter for formatting Telegram messages."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from src.presentation.telegram_bot.formatters.vehicle_formatter import VehicleFormatter
from src.presentation.telegram_bot.formatters.error_formatter import ErrorFormatter
from src.presentation.telegram_bot.formatters.premium_features_formatter import (
    PremiumFeaturesFormatter,
)


class InformationLevel(Enum):
    """Information disclosure levels for progressive enhancement."""

    ESSENTIAL = 1  # Essential info only (5-8 lines): Year, Make, Model, Body, Fuel
    STANDARD = 2  # Standard info (15-20 lines): + Engine, Transmission, Key Features
    DETAILED = (
        3  # Detailed info (30-40 lines): + Dimensions, Performance, Manufacturing
    )
    COMPLETE = 4  # Complete info: Everything available


class MessageAdapter:
    """Adapts domain objects to Telegram messages with smart formatting."""

    def __init__(self):
        """Initialize the message adapter."""
        self.default_level = InformationLevel.STANDARD

    def format_vehicle_response(
        self,
        vehicle_data: Dict[str, Any],
        level: InformationLevel = None,
        from_cache: bool = False,
    ) -> str:
        """Format vehicle data for Telegram message.

        Args:
            vehicle_data: Vehicle data from decoder
            level: Information disclosure level
            from_cache: Whether data is from cache

        Returns:
            Formatted message string
        """
        if not level:
            level = self.default_level

        # Extract attributes
        attrs = vehicle_data.get("attributes", {})
        if not attrs:
            return "❌ **Unable to parse vehicle data**\n\nPlease check the VIN and try again."

        # Determine service type
        service = vehicle_data.get("service", "NHTSA")
        is_autodev = service == "AutoDev"

        # Route to appropriate formatter based on level
        if level == InformationLevel.ESSENTIAL:
            return self._format_essential(attrs, is_autodev, from_cache)
        elif level == InformationLevel.STANDARD:
            return self._format_standard(attrs, is_autodev, from_cache)
        elif level == InformationLevel.DETAILED:
            return self._format_detailed(attrs, is_autodev, from_cache)
        else:  # COMPLETE
            return self._format_complete(attrs, is_autodev, from_cache)

    def _format_essential(
        self, attrs: Dict[str, Any], is_autodev: bool, from_cache: bool
    ) -> str:
        """Format essential vehicle information (5-8 lines)."""
        lines = []

        # Vehicle header with icon
        year = attrs.get("year", "")
        make = attrs.get("make", "")
        model = attrs.get("model", "")
        trim = attrs.get("trim", "")

        # Get body type for icon
        body = attrs.get("body_type" if is_autodev else "body", "")
        icon = self._get_vehicle_icon(body)

        # Create vehicle title
        vehicle_parts = [str(v) for v in [year, make, model, trim] if v]
        vehicle_title = (
            " ".join(vehicle_parts) if vehicle_parts else "Vehicle Information"
        )

        lines.append(f"{icon} **{vehicle_title}**")
        lines.append("━" * min(len(vehicle_title) + 2, 35))

        # Essential specs
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
            lines.append(f"🔹 **Quick Facts:** {' • '.join(specs)}")

        # Cache indicator
        if from_cache:
            lines.append("⚡ _Retrieved from cache_")

        # VIN at bottom
        vin = attrs.get("vin", "")
        if vin:
            lines.append(f"\n`{vin}`")

        return "\n".join(lines)

    def _format_standard(
        self, attrs: Dict[str, Any], is_autodev: bool, from_cache: bool
    ) -> str:
        """Format standard vehicle information (15-20 lines)."""
        lines = []

        # Start with essential info (without VIN)
        essential = self._format_essential(attrs, is_autodev, False)
        lines.extend(essential.split("\n")[:-1])  # Remove VIN line

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
            lines.append(f"• {' • '.join(features)}")
        else:
            lines.append("• Information not available")

        # Cache indicator
        if from_cache:
            lines.append("\n⚡ _Retrieved from cache_")

        # VIN at bottom
        vin = attrs.get("vin", "")
        if vin:
            lines.append(f"\n`{vin}`")

        return "\n".join(lines)

    def _format_detailed(
        self, attrs: Dict[str, Any], is_autodev: bool, from_cache: bool
    ) -> str:
        """Format detailed vehicle information (30-40 lines)."""
        lines = []

        # Start with standard info (without VIN)
        standard = self._format_standard(attrs, is_autodev, False)
        lines.extend(standard.split("\n")[:-1])  # Remove VIN line

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
                lines.append(f"• {' • '.join(dimensions)}")
            else:
                lines.append("• Dimension data not available")

        # Add Auto.dev specific features with premium formatting
        if is_autodev:
            # Create a data dict for the premium formatter
            vehicle_data = {"attributes": attrs}
            features_section = PremiumFeaturesFormatter.format_features_section(
                PremiumFeaturesFormatter.extract_features(vehicle_data)
            )
            if features_section:
                lines.append(features_section)

        # Add performance data
        lines.append("\n🏁 **Performance**")

        if is_autodev:
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

        # Cache indicator
        if from_cache:
            lines.append("\n⚡ _Retrieved from cache_")

        # VIN at bottom
        vin = attrs.get("vin", "")
        if vin:
            lines.append(f"\n`{vin}`")

        return "\n".join(lines)

    def _format_complete(
        self, attrs: Dict[str, Any], is_autodev: bool, from_cache: bool
    ) -> str:
        """Format complete vehicle information (all available data)."""
        lines = []

        # Vehicle header
        year = attrs.get("year", "")
        make = attrs.get("make", "")
        model = attrs.get("model", "")
        trim = attrs.get("trim", "")

        vehicle_desc = " ".join(str(v) for v in [year, make, model, trim] if v)
        body = attrs.get("body_type" if is_autodev else "body", "")
        icon = self._get_vehicle_icon(body)

        lines.append(
            f"{icon} **{vehicle_desc if vehicle_desc else 'Vehicle Information'}**"
        )
        lines.append("=" * 30)

        # VIN
        vin = attrs.get("vin", "")
        if vin:
            lines.append(f"**VIN:** `{vin}`")

        # Basic specs
        lines.append("\n📋 **BASIC SPECIFICATIONS**")
        lines.append("-" * 25)

        if is_autodev:
            self._add_field(lines, "Body Type", attrs.get("body_type"))
            self._add_field(lines, "Vehicle Style", attrs.get("vehicle_style"))
            self._add_field(lines, "Drive Type", attrs.get("drive_type"))
            self._add_field(lines, "Fuel Type", attrs.get("fuel_type"))
            self._add_field(lines, "EPA Class", attrs.get("epa_class"))
        else:
            self._add_field(lines, "Product Type", attrs.get("product_type"))
            self._add_field(lines, "Body Style", attrs.get("body"))
            self._add_field(lines, "Series", attrs.get("series"))
            self._add_field(lines, "Trim", attrs.get("trim"))
            self._add_field(lines, "Fuel Type", attrs.get("fuel_type"))
            self._add_field(lines, "Transmission", attrs.get("gears"))
            self._add_field(lines, "Drive Type", attrs.get("drive"))

        # Engine information
        lines.append("\n🔧 **ENGINE SPECIFICATIONS**")
        lines.append("-" * 25)

        if is_autodev:
            self._add_field(lines, "Engine", attrs.get("engine"))
            self._add_field(lines, "Configuration", attrs.get("configuration"))
            self._add_field(lines, "Cylinders", attrs.get("cylinders"))
            if attrs.get("displacement"):
                self._add_field(lines, "Displacement", f"{attrs.get('displacement')}L")
            if attrs.get("horsepower"):
                self._add_field(lines, "Horsepower", f"{attrs.get('horsepower')} HP")
            if attrs.get("torque"):
                self._add_field(lines, "Torque", f"{attrs.get('torque')} lb-ft")
        else:
            self._add_field(
                lines, "Engine Manufacturer", attrs.get("engine_manufacturer")
            )

        # Manufacturing (NHTSA only)
        if not is_autodev:
            lines.append("\n🏭 **MANUFACTURING**")
            lines.append("-" * 25)
            self._add_field(lines, "Manufacturer", attrs.get("manufacturer"))
            self._add_field(lines, "Plant Address", attrs.get("manufacturer_address"))
            self._add_field(lines, "Plant Country", attrs.get("plant_country"))

        # Dimensions (NHTSA only)
        if not is_autodev:
            lines.append("\n📏 **DIMENSIONS**")
            lines.append("-" * 25)
            if attrs.get("length_mm"):
                self._add_field(lines, "Length", f"{attrs.get('length_mm')} mm")
            if attrs.get("width_mm"):
                self._add_field(lines, "Width", f"{attrs.get('width_mm')} mm")
            if attrs.get("height_mm"):
                self._add_field(lines, "Height", f"{attrs.get('height_mm')} mm")
            if attrs.get("wheelbase_mm"):
                self._add_field(lines, "Wheelbase", f"{attrs.get('wheelbase_mm')} mm")
            if attrs.get("weight_empty_kg"):
                self._add_field(
                    lines, "Empty Weight", f"{attrs.get('weight_empty_kg')} kg"
                )

        # Performance
        lines.append("\n🏁 **PERFORMANCE**")
        lines.append("-" * 25)

        if is_autodev:
            mpg_city = attrs.get("mpg_city")
            mpg_highway = attrs.get("mpg_highway")
            if mpg_city:
                self._add_field(lines, "City MPG", mpg_city)
            if mpg_highway:
                self._add_field(lines, "Highway MPG", mpg_highway)
        else:
            if attrs.get("max_speed_kmh"):
                self._add_field(
                    lines, "Max Speed", f"{attrs.get('max_speed_kmh')} km/h"
                )
            if attrs.get("avg_co2_emission_g_km"):
                self._add_field(
                    lines, "CO2 Emission", f"{attrs.get('avg_co2_emission_g_km')} g/km"
                )

        # Features
        lines.append("\n✨ **FEATURES**")
        lines.append("-" * 25)

        if is_autodev:
            features = attrs.get("features", [])
            if features:
                for feature in features:
                    lines.append(f"• {feature}")
            else:
                lines.append("No feature data available")
        else:
            self._add_field(lines, "Doors", attrs.get("no_of_doors"))
            self._add_field(lines, "Seats", attrs.get("no_of_seats"))
            self._add_field(lines, "Axles", attrs.get("no_of_axels"))
            self._add_field(lines, "ABS", attrs.get("abs"))
            self._add_field(lines, "Steering Type", attrs.get("steering_type"))
            self._add_field(lines, "Front Suspension", attrs.get("front_suspension"))
            self._add_field(lines, "Rear Suspension", attrs.get("rear_suspension"))

        # Colors (Auto.dev only)
        if is_autodev:
            colors = attrs.get("colors", [])
            if colors:
                lines.append("\n🎨 **AVAILABLE COLORS**")
                lines.append("-" * 25)
                for color in colors:
                    lines.append(f"• {color}")

        # Cache indicator
        if from_cache:
            lines.append("\n⚡ _Retrieved from cache_")

        return "\n".join(lines)

    def format_error_message(self, error: str, vin: Optional[str] = None) -> str:
        """Format an error message.

        Args:
            error: Error message
            vin: Optional VIN that caused the error

        Returns:
            Formatted error message
        """
        lines = ["❌ **Error**", ""]

        if vin:
            lines.append(f"VIN: `{vin}`")
            lines.append("")

        lines.append(error)
        lines.append("")
        lines.append(
            "Please check the VIN and try again, or contact support if the issue persists."
        )

        return "\n".join(lines)

    def format_welcome_message(
        self,
        user_name: Optional[str] = None,
        has_api_key: bool = False,
        preferred_service: str = "autodev",
    ) -> str:
        """Format welcome message.

        Args:
            user_name: Optional user name
            has_api_key: Whether user has API key configured
            preferred_service: User's preferred decoder service

        Returns:
            Formatted welcome message
        """
        lines = []

        if user_name:
            lines.append(f"🚗 **Welcome back, {user_name}!**")
        else:
            lines.append("🚗 **Welcome to VIN Decoder Bot!**")

        lines.append("")
        lines.append(
            "I can decode Vehicle Identification Numbers (VINs) using official databases."
        )
        lines.append("")
        lines.append("**How to use:**")
        lines.append("• Send me a 17-character VIN directly")
        lines.append("• Use /vin <VIN> command")
        lines.append("")
        lines.append("**Other commands:**")
        lines.append("/help - Show all commands")
        lines.append("/settings - Configure decoder service")
        lines.append("/history - View your recent searches")

        if preferred_service == "autodev" and has_api_key:
            lines.append("")
            lines.append(f"✅ Using Auto.dev service with your API key")
        elif preferred_service == "autodev" and not has_api_key:
            lines.append("")
            lines.append("⚠️ Auto.dev selected but no API key configured")
            lines.append("Use /settings to add your API key")
        else:
            lines.append("")
            lines.append(f"ℹ️ Using {preferred_service.upper()} service")

        return "\n".join(lines)

    def format_history_entry(
        self, vin: str, vehicle_info: Dict[str, Any], decoded_at: str, index: int
    ) -> str:
        """Format a single history entry.

        Args:
            vin: Vehicle VIN
            vehicle_info: Vehicle information
            decoded_at: When it was decoded
            index: Entry index number

        Returns:
            Formatted history entry
        """
        year = vehicle_info.get("year", "")
        make = vehicle_info.get("make", "")
        model = vehicle_info.get("model", "")

        vehicle_desc = " ".join(str(v) for v in [year, make, model] if v)
        if not vehicle_desc:
            vehicle_desc = "Unknown Vehicle"

        lines = [
            f"{index}. **{vehicle_desc}**",
            f"   VIN: `{vin}`",
            f"   Date: {decoded_at}",
        ]

        return "\n".join(lines)

    def _get_vehicle_icon(self, body_type: str) -> str:
        """Get appropriate emoji icon based on vehicle body type.

        Args:
            body_type: Vehicle body type

        Returns:
            Emoji icon
        """
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

    def _add_field(self, lines: List[str], label: str, value: Any) -> None:
        """Add a field to the message if it has a value.

        Args:
            lines: List of message lines
            label: Field label
            value: Field value
        """
        if value and value != "":
            lines.append(f"**{label}:** {value}")
