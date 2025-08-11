"""Unit tests for VIN-related value objects."""

import pytest
from src.domain.vehicle.value_objects.vin_number import VINNumber
from src.domain.vehicle.value_objects.model_year import ModelYear
from src.domain.vehicle.value_objects.decode_result import DecodeResult
from src.tests.utils.factories import VINFactory


class TestVINNumber:
    """Test VINNumber value object."""
    
    def test_create_valid_vin(self):
        """Test creating a valid VIN number."""
        valid_vin = "1HGBH41JXMN109186"
        vin = VINNumber(valid_vin)
        assert vin.value == valid_vin
        assert str(vin) == valid_vin
        assert vin.is_valid()
    
    def test_normalize_vin(self):
        """Test VIN normalization (uppercase, strip whitespace)."""
        test_cases = [
            ("1hgbh41jxmn109186", "1HGBH41JXMN109186"),
            ("  1HGBH41JXMN109186  ", "1HGBH41JXMN109186"),
            ("1HgBh41JxMn109186", "1HGBH41JXMN109186"),
        ]
        
        for input_vin, expected in test_cases:
            vin = VINNumber(input_vin)
            assert vin.value == expected
    
    def test_invalid_vin_length(self):
        """Test that invalid VIN lengths raise ValueError."""
        invalid_vins = [
            "ABC123",  # Too short
            "1234567890ABCDEFGH",  # Too long
            "",  # Empty
            "12345678901234567890",  # Way too long
        ]
        
        for invalid_vin in invalid_vins:
            with pytest.raises(ValueError, match="VIN must be exactly 17 characters"):
                VINNumber(invalid_vin)
    
    def test_invalid_vin_characters(self):
        """Test that invalid characters in VIN raise ValueError."""
        invalid_vins = [
            "1HGBH41JXMN10918I",  # Contains I
            "1HGBH41JXMN10918O",  # Contains O
            "1HGBH41JXMN10918Q",  # Contains Q
            "1HGBH41JXMN10918!",  # Contains special character
            "1HGBH41JXM 109186",  # Contains space in middle
        ]
        
        for invalid_vin in invalid_vins:
            with pytest.raises(ValueError, match="VIN contains invalid characters|VIN must be exactly"):
                VINNumber(invalid_vin)
    
    def test_vin_equality(self):
        """Test VIN equality comparison."""
        vin1 = VINNumber("1HGBH41JXMN109186")
        vin2 = VINNumber("1HGBH41JXMN109186")
        vin3 = VINNumber("WBANE53517C123456")
        
        assert vin1 == vin2
        assert vin1 != vin3
        assert vin1 != "1HGBH41JXMN109186"  # Not equal to string
    
    def test_vin_hash(self):
        """Test VIN hashing for use in sets/dicts."""
        vin1 = VINNumber("1HGBH41JXMN109186")
        vin2 = VINNumber("1HGBH41JXMN109186")
        vin3 = VINNumber("WBANE53517C123456")
        
        assert hash(vin1) == hash(vin2)
        assert hash(vin1) != hash(vin3)
        
        # Test in set
        vin_set = {vin1, vin2, vin3}
        assert len(vin_set) == 2
    
    def test_vin_repr(self):
        """Test VIN representation."""
        vin = VINNumber("1HGBH41JXMN109186")
        assert repr(vin) == "VINNumber('1HGBH41JXMN109186')"
    
    def test_get_manufacturer_code(self):
        """Test extracting manufacturer code from VIN."""
        test_cases = [
            ("1HGBH41JXMN109186", "1HG"),  # Honda
            ("WBANE53517C123456", "WBA"),  # BMW
            ("5YJSA1DN5DF123456", "5YJ"),  # Tesla
        ]
        
        for vin_str, expected_code in test_cases:
            vin = VINNumber(vin_str)
            assert vin.get_manufacturer_code() == expected_code
    
    def test_get_year_code(self):
        """Test extracting year code from VIN."""
        test_cases = [
            ("1HGBH41JXMN109186", "M"),  # 2021
            ("WBANE53517C123456", "7"),  # 2007
            ("5YJSA1DN5DF123456", "D"),  # 2013
        ]
        
        for vin_str, expected_code in test_cases:
            vin = VINNumber(vin_str)
            assert vin.get_year_code() == expected_code
    
    @pytest.mark.parametrize("vin_str", [
        VINFactory.create_valid_vin(i) for i in range(5)
    ])
    def test_factory_generated_vins(self, vin_str):
        """Test that factory-generated VINs are valid."""
        vin = VINNumber(vin_str)
        assert vin.is_valid()


class TestModelYear:
    """Test ModelYear value object."""
    
    def test_create_valid_year(self):
        """Test creating a valid model year."""
        year = ModelYear(2021)
        assert year.value == 2021
        assert str(year) == "2021"
        assert year.is_valid()
    
    def test_invalid_year_too_old(self):
        """Test that years before 1980 raise ValueError."""
        with pytest.raises(ValueError, match="Model year must be between 1980"):
            ModelYear(1979)
    
    def test_invalid_year_future(self):
        """Test that years too far in future raise ValueError."""
        from datetime import datetime
        future_year = datetime.now().year + 3
        with pytest.raises(ValueError, match="Model year must be between 1980"):
            ModelYear(future_year)
    
    def test_year_equality(self):
        """Test ModelYear equality comparison."""
        year1 = ModelYear(2021)
        year2 = ModelYear(2021)
        year3 = ModelYear(2022)
        
        assert year1 == year2
        assert year1 != year3
        assert year1 != 2021  # Not equal to int
    
    def test_year_comparison(self):
        """Test ModelYear comparison operations."""
        year1 = ModelYear(2020)
        year2 = ModelYear(2021)
        year3 = ModelYear(2021)
        
        assert year1 < year2
        assert year2 > year1
        assert year2 >= year3
        assert year2 <= year3
    
    def test_year_hash(self):
        """Test ModelYear hashing."""
        year1 = ModelYear(2021)
        year2 = ModelYear(2021)
        year3 = ModelYear(2022)
        
        assert hash(year1) == hash(year2)
        assert hash(year1) != hash(year3)
    
    def test_year_repr(self):
        """Test ModelYear representation."""
        year = ModelYear(2021)
        assert repr(year) == "ModelYear(2021)"
    
    def test_get_age(self):
        """Test calculating vehicle age from model year."""
        from datetime import datetime
        current_year = datetime.now().year
        year = ModelYear(current_year - 5)
        assert year.get_age() == 5
    
    def test_is_classic(self):
        """Test determining if vehicle is classic (25+ years old)."""
        from datetime import datetime
        current_year = datetime.now().year
        
        classic_year = ModelYear(current_year - 26)
        assert classic_year.is_classic()
        
        not_classic_year = ModelYear(current_year - 24)
        assert not not_classic_year.is_classic()


class TestDecodeResult:
    """Test DecodeResult value object."""
    
    def test_create_successful_result(self):
        """Test creating a successful decode result."""
        result = DecodeResult(
            success=True,
            vin="1HGBH41JXMN109186",
            manufacturer="Honda",
            model="Civic",
            model_year=2021,
            attributes={
                "engine": "1.5L",
                "transmission": "CVT"
            },
            service_used="nhtsa",
            raw_response={"test": "data"}
        )
        
        assert result.success is True
        assert result.vin == "1HGBH41JXMN109186"
        assert result.manufacturer == "Honda"
        assert result.model == "Civic"
        assert result.model_year == 2021
        assert result.attributes["engine"] == "1.5L"
        assert result.service_used == "nhtsa"
        assert result.error_message is None
    
    def test_create_failed_result(self):
        """Test creating a failed decode result."""
        result = DecodeResult(
            success=False,
            vin="INVALID123",
            error_message="Invalid VIN format",
            service_used="nhtsa"
        )
        
        assert result.success is False
        assert result.vin == "INVALID123"
        assert result.error_message == "Invalid VIN format"
        assert result.manufacturer is None
        assert result.model is None
        assert result.attributes == {}
    
    def test_result_equality(self):
        """Test DecodeResult equality comparison."""
        result1 = DecodeResult(
            success=True,
            vin="1HGBH41JXMN109186",
            manufacturer="Honda",
            model="Civic",
            model_year=2021,
            service_used="nhtsa"
        )
        
        result2 = DecodeResult(
            success=True,
            vin="1HGBH41JXMN109186",
            manufacturer="Honda",
            model="Civic",
            model_year=2021,
            service_used="nhtsa"
        )
        
        result3 = DecodeResult(
            success=True,
            vin="WBANE53517C123456",
            manufacturer="BMW",
            model="5 Series",
            model_year=2007,
            service_used="nhtsa"
        )
        
        assert result1 == result2
        assert result1 != result3
    
    def test_to_dict(self):
        """Test converting DecodeResult to dictionary."""
        result = DecodeResult(
            success=True,
            vin="1HGBH41JXMN109186",
            manufacturer="Honda",
            model="Civic",
            model_year=2021,
            attributes={
                "engine": "1.5L",
                "transmission": "CVT"
            },
            service_used="nhtsa"
        )
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["vin"] == "1HGBH41JXMN109186"
        assert result_dict["manufacturer"] == "Honda"
        assert result_dict["model"] == "Civic"
        assert result_dict["model_year"] == 2021
        assert result_dict["attributes"]["engine"] == "1.5L"
        assert result_dict["service_used"] == "nhtsa"
    
    def test_from_dict(self):
        """Test creating DecodeResult from dictionary."""
        data = {
            "success": True,
            "vin": "1HGBH41JXMN109186",
            "manufacturer": "Honda",
            "model": "Civic",
            "model_year": 2021,
            "attributes": {
                "engine": "1.5L",
                "transmission": "CVT"
            },
            "service_used": "nhtsa"
        }
        
        result = DecodeResult.from_dict(data)
        assert result.success is True
        assert result.vin == "1HGBH41JXMN109186"
        assert result.manufacturer == "Honda"
        assert result.model == "Civic"
        assert result.model_year == 2021
        assert result.attributes["engine"] == "1.5L"
    
    def test_get_display_string(self):
        """Test getting display string for decode result."""
        result = DecodeResult(
            success=True,
            vin="1HGBH41JXMN109186",
            manufacturer="Honda",
            model="Civic",
            model_year=2021,
            service_used="nhtsa"
        )
        
        display = result.get_display_string()
        assert "2021 Honda Civic" in display
        assert "1HGBH41JXMN109186" in display
    
    def test_has_complete_data(self):
        """Test checking if decode result has complete data."""
        complete_result = DecodeResult(
            success=True,
            vin="1HGBH41JXMN109186",
            manufacturer="Honda",
            model="Civic",
            model_year=2021,
            attributes={"engine": "1.5L"},
            service_used="nhtsa"
        )
        assert complete_result.has_complete_data()
        
        incomplete_result = DecodeResult(
            success=True,
            vin="1HGBH41JXMN109186",
            manufacturer="Honda",
            model=None,  # Missing model
            model_year=2021,
            service_used="nhtsa"
        )
        assert not incomplete_result.has_complete_data()