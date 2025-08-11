"""Simple test to verify basic testing setup."""

import pytest
from src.domain.vehicle.value_objects.vin_number import VINNumber


def test_vin_creation():
    """Test that we can create a VIN number."""
    vin = VINNumber("1HGBH41JXMN109186")
    assert vin.value == "1HGBH41JXMN109186"
    assert vin.is_valid()


def test_vin_invalid():
    """Test that invalid VIN raises error."""
    with pytest.raises(ValueError):
        VINNumber("INVALID")