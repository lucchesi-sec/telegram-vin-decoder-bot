from typing import Any, Dict, List


def _first(*values: Any) -> Any:
    for v in values:
        if v not in (None, ""):
            return v
    return None


def format_vehicle_summary(data: Dict[str, Any]) -> str:
    # Heuristic field extraction; adjust to your plan/endpoint payload
    # Try common keys found in typical VIN decoders
    # Handle both direct attributes and nested attributes structure
    if isinstance(data, dict) and "attributes" in data:
        attrs = data["attributes"]
    else:
        attrs = data if isinstance(data, dict) else {}

    year = _first(attrs.get("year"), attrs.get("Year"))
    make = _first(attrs.get("make"), attrs.get("Make"))
    model = _first(attrs.get("model"), attrs.get("Model"))
    trim = _first(attrs.get("trim"), attrs.get("Trim"))
    body = _first(attrs.get("body_type"), attrs.get("Body"), attrs.get("body"))
    engine = _first(
        attrs.get("engine"),
        attrs.get("Engine"),
        attrs.get("engine_type"),
        attrs.get("engineSize"),
    )
    transmission = _first(attrs.get("transmission"), attrs.get("Transmission"))
    drive = _first(attrs.get("drive_type"), attrs.get("DriveType"), attrs.get("drive"))
    fuel = _first(attrs.get("fuel_type"), attrs.get("FuelType"), attrs.get("fuel"))
    plant = _first(attrs.get("plant_country"), attrs.get("PlantCountry"), attrs.get("manufacturer"))
    vin = _first(attrs.get("vin"), attrs.get("VIN"))

    lines: List[str] = []
    title_parts = [str(p) for p in (year, make, model) if p]
    if title_parts:
        lines.append("Vehicle: " + " ".join(title_parts))
    if trim:
        lines.append(f"Trim: {trim}")
    if body:
        lines.append(f"Body: {body}")
    if engine:
        lines.append(f"Engine: {engine}")
    if transmission:
        lines.append(f"Transmission: {transmission}")
    if drive:
        lines.append(f"Drive: {drive}")
    if fuel:
        lines.append(f"Fuel: {fuel}")
    if plant:
        lines.append(f"Plant/Manufacturer: {plant}")
    if vin:
        lines.append(f"VIN: {vin}")

    if not lines:
        # Fallback
        return "Could not parse vehicle fields from response."

    return "\n".join(lines)

