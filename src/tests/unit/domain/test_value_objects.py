"""Unit tests for domain value objects."""

import pytest
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.domain.vehicle.value_objects.vin_number import VINNumber
from src.domain.vehicle.value_objects.model_year import ModelYear
from src.domain.vehicle.value_objects.decode_result import DecodeResult


@pytest.mark.unit
@pytest.mark.domain
class TestTelegramID:
    """Test cases for TelegramID value object."""
    
    def test_telegram_id_creation_valid(self):
        """Test creating a valid TelegramID."""
        # Arrange
        valid_id = 123456789
        
        # Act
        telegram_id = TelegramID(valid_id)
        
        # Assert
        assert telegram_id.value == valid_id
    
    def test_telegram_id_equality(self):
        """Test TelegramID equality comparison."""
        # Arrange
        id_value = 123456789
        telegram_id1 = TelegramID(id_value)
        telegram_id2 = TelegramID(id_value)
        telegram_id3 = TelegramID(987654321)
        
        # Assert
        assert telegram_id1 == telegram_id2
        assert telegram_id1 != telegram_id3
    
    def test_telegram_id_string_representation(self):
        """Test TelegramID string representation."""
        # Arrange
        id_value = 123456789
        telegram_id = TelegramID(id_value)
        
        # Act & Assert
        assert str(telegram_id) == str(id_value)
    
    @pytest.mark.parametrize("invalid_id", [
        0,           # Zero
        -1,          # Negative
        None,        # None
        "123456789", # String
    ])
    def test_telegram_id_validation_invalid(self, invalid_id):
        """Test TelegramID validation with invalid values."""
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            TelegramID(invalid_id)


@pytest.mark.unit
@pytest.mark.domain
class TestUserPreferences:
    """Test cases for UserPreferences value object."""
    
    def test_user_preferences_creation_with_defaults(self):
        """Test creating UserPreferences with default values."""
        # Act
        preferences = UserPreferences()
        
        # Assert
        assert preferences.preferred_decoder == "nhtsa"
        assert preferences.include_market_value is True
        assert preferences.include_history is False
        assert preferences.include_recalls is True
        assert preferences.include_specs is True
        assert preferences.format_preference == "standard"
    
    def test_user_preferences_creation_with_custom_values(self):
        """Test creating UserPreferences with custom values."""
        # Act
        preferences = UserPreferences(
            preferred_decoder="autodev",
            include_market_value=False,
            include_history=True,
            include_recalls=False,
            include_specs=False,
            format_preference="detailed"
        )
        
        # Assert
        assert preferences.preferred_decoder == "autodev"
        assert preferences.include_market_value is False
        assert preferences.include_history is True
        assert preferences.include_recalls is False
        assert preferences.include_specs is False
        assert preferences.format_preference == "detailed"
    
    def test_user_preferences_to_dict(self):
        """Test converting UserPreferences to dictionary."""
        # Arrange
        preferences = UserPreferences(
            preferred_decoder="autodev",
            include_market_value=False
        )
        
        # Act
        preferences_dict = preferences.to_dict()
        
        # Assert
        assert isinstance(preferences_dict, dict)
        assert preferences_dict["preferred_decoder"] == "autodev"
        assert preferences_dict["include_market_value"] is False
        assert "include_history" in preferences_dict
        assert "include_recalls" in preferences_dict
        assert "include_specs" in preferences_dict
        assert "format_preference" in preferences_dict
    
    def test_user_preferences_equality(self):
        """Test UserPreferences equality comparison."""
        # Arrange
        preferences1 = UserPreferences(preferred_decoder="nhtsa")
        preferences2 = UserPreferences(preferred_decoder="nhtsa")
        preferences3 = UserPreferences(preferred_decoder="autodev")
        
        # Assert
        assert preferences1 == preferences2
        assert preferences1 != preferences3
    
    @pytest.mark.parametrize("decoder", ["nhtsa", "autodev", "carsxe"])
    def test_user_preferences_valid_decoders(self, decoder):
        """Test UserPreferences with valid decoder options."""
        # Act
        preferences = UserPreferences(preferred_decoder=decoder)
        
        # Assert
        assert preferences.preferred_decoder == decoder
    
    @pytest.mark.parametrize("format_pref", ["standard", "detailed", "compact"])
    def test_user_preferences_valid_formats(self, format_pref):
        """Test UserPreferences with valid format preferences."""
        # Act
        preferences = UserPreferences(format_preference=format_pref)
        
        # Assert
        assert preferences.format_preference == format_pref


@pytest.mark.unit
@pytest.mark.domain
class TestVINNumber:
    """Test cases for VINNumber value object."""
    
    def test_vin_number_creation_valid(self):
        """Test creating a valid VINNumber."""
        # Arrange
        valid_vin = "1HGBH41JXMN109186"
        
        # Act
        vin = VINNumber(valid_vin)
        
        # Assert
        assert vin.value == valid_vin
    
    def test_vin_number_equality(self):
        """Test VINNumber equality comparison."""
        # Arrange
        vin_value = "1HGBH41JXMN109186"
        vin1 = VINNumber(vin_value)
        vin2 = VINNumber(vin_value)
        vin3 = VINNumber("JH4KA8260MC000000")
        
        # Assert
        assert vin1 == vin2
        assert vin1 != vin3
    
    def test_vin_number_string_representation(self):
        """Test VINNumber string representation."""
        # Arrange
        vin_value = "1HGBH41JXMN109186"
        vin = VINNumber(vin_value)
        
        # Act & Assert
        assert str(vin) == vin_value
    
    @pytest.mark.parametrize("valid_vin", [
        "1HGBH41JXMN109186",  # Honda Civic
        "JH4KA8260MC000000",  # Acura Legend
        "WBAWN13506CP00000",  # BMW X5
        "5YFBU4EE8EP000000",  # Toyota Camry
    ])
    def test_vin_number_valid_vins(self, valid_vin):
        """Test VINNumber with various valid VINs."""
        # Act
        vin = VINNumber(valid_vin)
        
        # Assert
        assert vin.value == valid_vin
        assert len(vin.value) == 17
    
    @pytest.mark.parametrize("invalid_vin", [
        "",                    # Empty string
        "123",                 # Too short
        "1" * 18,             # Too long
        "1HGBH41JXMN10918I",  # Contains 'I'
        "1HGBH41JXMN10918O",  # Contains 'O'
        "1HGBH41JXMN10918Q",  # Contains 'Q'
        None,                  # None
        123456789,            # Integer
    ])
    def test_vin_number_validation_invalid(self, invalid_vin):
        """Test VINNumber validation with invalid values."""
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            VINNumber(invalid_vin)


@pytest.mark.unit
@pytest.mark.domain
class TestModelYear:
    """Test cases for ModelYear value object."""
    
    def test_model_year_creation_valid(self):
        """Test creating a valid ModelYear."""
        # Arrange
        valid_year = 2021
        
        # Act
        model_year = ModelYear(valid_year)
        
        # Assert
        assert model_year.value == valid_year
    
    def test_model_year_equality(self):
        """Test ModelYear equality comparison."""
        # Arrange
        year = 2021
        model_year1 = ModelYear(year)
        model_year2 = ModelYear(year)
        model_year3 = ModelYear(2020)
        
        # Assert
        assert model_year1 == model_year2
        assert model_year1 != model_year3
    
    def test_model_year_string_representation(self):
        """Test ModelYear string representation."""
        # Arrange
        year = 2021
        model_year = ModelYear(year)
        
        # Act & Assert
        assert str(model_year) == str(year)
    
    @pytest.mark.parametrize("valid_year", [
        1980,  # Minimum valid year
        2000,  # Y2K
        2021,  # Recent year
        2025,  # Future year (within reason)
    ])
    def test_model_year_valid_years(self, valid_year):
        """Test ModelYear with various valid years."""
        # Act
        model_year = ModelYear(valid_year)
        
        # Assert
        assert model_year.value == valid_year
    
    @pytest.mark.parametrize("invalid_year", [
        1979,     # Too old
        2030,     # Too far in future
        0,        # Zero
        -1,       # Negative
        None,     # None
        "2021",   # String
    ])
    def test_model_year_validation_invalid(self, invalid_year):
        """Test ModelYear validation with invalid values."""
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            ModelYear(invalid_year)


@pytest.mark.unit
@pytest.mark.domain
class TestDecodeResult:
    """Test cases for DecodeResult value object."""
    
    def test_decode_result_creation_success(self, sample_vin):
        """Test creating a successful DecodeResult."""
        # Arrange
        data = {"make": "Honda", "model": "Civic", "year": 2021}
        service_used = "nhtsa"
        
        # Act
        result = DecodeResult(
            vin=sample_vin,
            success=True,
            data=data,
            service_used=service_used
        )
        
        # Assert
        assert result.vin == sample_vin
        assert result.success is True
        assert result.data == data
        assert result.service_used == service_used
        assert result.error_message is None
    
    def test_decode_result_creation_failure(self, sample_vin):
        """Test creating a failed DecodeResult."""
        # Arrange
        error_message = "API rate limit exceeded"
        service_used = "autodev"
        
        # Act
        result = DecodeResult(
            vin=sample_vin,
            success=False,
            data=None,
            service_used=service_used,
            error_message=error_message
        )
        
        # Assert
        assert result.vin == sample_vin
        assert result.success is False
        assert result.data is None
        assert result.service_used == service_used
        assert result.error_message == error_message
    
    def test_decode_result_equality(self, sample_vin):
        """Test DecodeResult equality comparison."""
        # Arrange
        data = {"make": "Honda"}
        result1 = DecodeResult(
            vin=sample_vin,
            success=True,
            data=data,
            service_used="nhtsa"
        )
        result2 = DecodeResult(
            vin=sample_vin,
            success=True,
            data=data,
            service_used="nhtsa"
        )
        result3 = DecodeResult(
            vin=sample_vin,
            success=False,
            data=None,
            service_used="autodev"
        )
        
        # Assert
        assert result1 == result2
        assert result1 != result3
    
    def test_decode_result_with_empty_data(self, sample_vin):
        """Test DecodeResult with empty data."""
        # Act
        result = DecodeResult(
            vin=sample_vin,
            success=True,
            data={},
            service_used="nhtsa"
        )
        
        # Assert
        assert result.data == {}
        assert result.success is True
    
    def test_decode_result_immutability(self, sample_vin):
        """Test that DecodeResult data is immutable by reference."""
        # Arrange
        original_data = {"make": "Honda", "model": "Civic"}
        result = DecodeResult(
            vin=sample_vin,
            success=True,
            data=original_data,
            service_used="nhtsa"
        )
        
        # Act - Modify original data
        original_data["make"] = "Toyota"
        
        # Assert - Result should still have original data
        # Note: This test assumes the implementation copies the data
        # If not implemented, this test will guide the implementation
        assert result.data["make"] == "Honda"

