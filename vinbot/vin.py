import re


VIN_REGEX = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$", re.IGNORECASE)


def normalize_vin(vin: str) -> str:
    return vin.strip().upper()


def is_valid_vin(vin: str) -> bool:
    return bool(VIN_REGEX.match(normalize_vin(vin)))

