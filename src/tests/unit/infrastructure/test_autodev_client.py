"""Unit tests for AutoDevClient."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from src.infrastructure.external_services.autodev.autodev_client import AutoDevClient
from src.domain.vehicle.value_objects.vin_number import VINNumber


@pytest.mark.unit
@pytest.mark.infrastructure
class TestAutoDevClient:
    """Test cases for AutoDevClient."""
    
    @pytest.fixture
    def autodev_client(self):
        """Create AutoDevClient instance."""
        return AutoDevClient(
            api_key="test_api_key_12345",
            timeout=15
        )
    
    @pytest.fixture
    def sample_autodev_api_response(self):
        """Sample AutoDev API response."""
        return {
            "vin": "1HGBH41JXMN109186",
            "make": {"name": "Honda"},
            "model": {"name": "Civic"},
            "years": [{"year": 2021}],
            "engine": {
                "name": "1.5L I4",
                "cylinder": 4,
                "size": "1.5L",
                "fuelType": "Gasoline",
                "horsepower": 180,
                "torque": 177,
                "configuration": "Inline",
                "compressorType": "Turbo"
            },
            "transmission": {
                "name": "CVT",
                "transmissionType": "Automatic",
                "numberOfSpeeds": "Variable",
                "automaticType": "CVT"
            },
            "categories": {
                "primaryBodyType": "Sedan",
                "vehicleStyle": "4-Door Sedan",
                "vehicleSize": "Compact",
                "epaClass": "Compact Cars"
            },
            "mpg": {
                "city": 32,
                "highway": 42
            },
            "drivenWheels": "Front-Wheel Drive",
            "numOfDoors": 4
        }
    
    def test_autodev_client_initialization(self):
        """Test AutoDevClient initialization."""
        # Arrange
        api_key = "test_key"
        timeout = 30
        
        # Act
        client = AutoDevClient(api_key=api_key, timeout=timeout)
        
        # Assert
        assert client.api_key == api_key
        assert client.timeout == timeout
        assert client.service_name == "AutoDev"
        assert client.BASE_URL == "https://auto.dev/api"
    
    @patch('httpx.AsyncClient')
    async def test_decode_vin_success(
        self,
        mock_async_client,
        autodev_client,
        sample_vin,
        sample_autodev_api_response
    ):
        """Test successful VIN decoding."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_autodev_api_response
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act
        result = await autodev_client.decode_vin(sample_vin)
        
        # Assert
        assert result["success"] is True
        assert result["vin"] == sample_vin.value
        assert result["service"] == "AutoDev"
        assert "attributes" in result
        assert result["attributes"]["make"] == "Honda"
        assert result["attributes"]["model"] == "Civic"
        assert result["attributes"]["year"] == 2021
        
        # Verify API call
        expected_url = f"https://auto.dev/api/vin/{sample_vin.value}"
        mock_client_instance.get.assert_called_once_with(
            expected_url,
            headers={
                "Authorization": f"Bearer {autodev_client.api_key}",
                "Accept": "application/json"
            }
        )
    
    @patch('httpx.AsyncClient')
    async def test_decode_vin_unauthorized(
        self,
        mock_async_client,
        autodev_client,
        sample_vin
    ):
        """Test VIN decoding with unauthorized response."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status_code = 401
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await autodev_client.decode_vin(sample_vin)
        
        assert "Invalid API key or unauthorized access" in str(exc_info.value)
    
    @patch('httpx.AsyncClient')
    async def test_decode_vin_not_found(
        self,
        mock_async_client,
        autodev_client,
        sample_vin
    ):
        """Test VIN decoding with VIN not found response."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await autodev_client.decode_vin(sample_vin)
        
        assert "VIN not found or invalid" in str(exc_info.value)
    
    @patch('httpx.AsyncClient')
    async def test_decode_vin_client_error(
        self,
        mock_async_client,
        autodev_client,
        sample_vin
    ):
        """Test VIN decoding with client error response."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status_code = 429  # Rate limit
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await autodev_client.decode_vin(sample_vin)
        
        assert "API error: 429" in str(exc_info.value)
    
    @patch('httpx.AsyncClient')
    async def test_decode_vin_http_status_error(
        self,
        mock_async_client,
        autodev_client,
        sample_vin
    ):
        """Test VIN decoding with HTTP status error."""
        # Arrange
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = httpx.HTTPStatusError(
            "500 Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500)
        )
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await autodev_client.decode_vin(sample_vin)
        
        assert "Auto.dev API error: 500" in str(exc_info.value)
    
    @patch('httpx.AsyncClient')
    async def test_decode_vin_request_error(
        self,
        mock_async_client,
        autodev_client,
        sample_vin
    ):
        """Test VIN decoding with request error."""
        # Arrange
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = httpx.RequestError("Connection timeout")
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await autodev_client.decode_vin(sample_vin)
        
        assert "Network error: Connection timeout" in str(exc_info.value)
    
    @patch('httpx.AsyncClient')
    async def test_decode_vin_unexpected_error(
        self,
        mock_async_client,
        autodev_client,
        sample_vin
    ):
        """Test VIN decoding with unexpected error."""
        # Arrange
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = ValueError("Unexpected error")
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await autodev_client.decode_vin(sample_vin)
        
        assert "Failed to decode VIN: Unexpected error" in str(exc_info.value)
    
    def test_format_response_complete_data(self, autodev_client, sample_autodev_api_response):
        """Test formatting complete AutoDev response data."""
        # Act
        result = autodev_client.format_response(sample_autodev_api_response)
        
        # Assert
        assert result["success"] is True
        assert result["vin"] == "1HGBH41JXMN109186"
        assert result["service"] == "AutoDev"
        assert "attributes" in result
        
        attributes = result["attributes"]
        assert attributes["make"] == "Honda"
        assert attributes["model"] == "Civic"
        assert attributes["year"] == 2021
        assert attributes["engine"] == "1.5L I4"
        assert attributes["cylinders"] == 4
        assert attributes["displacement"] == "1.5L"
        assert attributes["fuel_type"] == "Gasoline"
        assert attributes["horsepower"] == 180
        assert attributes["torque"] == 177
        assert attributes["transmission"] == "CVT"
        assert attributes["drive_type"] == "Front-Wheel Drive"
        assert attributes["doors"] == 4
        assert attributes["body_type"] == "Sedan"
        assert attributes["mpg_city"] == 32
        assert attributes["mpg_highway"] == 42
    
    def test_format_response_minimal_data(self, autodev_client):
        """Test formatting minimal AutoDev response data."""
        # Arrange
        minimal_response = {
            "vin": "1HGBH41JXMN109186",
            "make": "Honda",
            "model": "Civic"
        }
        
        # Act
        result = autodev_client.format_response(minimal_response)
        
        # Assert
        assert result["success"] is True
        assert result["vin"] == "1HGBH41JXMN109186"
        assert result["service"] == "AutoDev"
        
        attributes = result["attributes"]
        assert attributes["make"] == "Honda"
        assert attributes["model"] == "Civic"
        # Should not have fields that weren't in the response
        assert "year" not in attributes
        assert "engine" not in attributes
    
    def test_format_response_with_options_and_colors(self, autodev_client):
        """Test formatting response with options and colors."""
        # Arrange
        response_with_options = {
            "vin": "1HGBH41JXMN109186",
            "make": {"name": "Honda"},
            "options": [
                {
                    "categoryName": "Safety",
                    "options": [
                        {"name": "Anti-lock Braking System"},
                        {"name": "Electronic Stability Control"}
                    ]
                }
            ],
            "colors": [
                {
                    "categoryName": "Exterior Colors",
                    "options": [
                        {"name": "Crystal Black Pearl"},
                        {"name": "Platinum White Pearl"}
                    ]
                }
            ]
        }
        
        # Act
        result = autodev_client.format_response(response_with_options)
        
        # Assert
        attributes = result["attributes"]
        assert "features" in attributes
        assert "Anti-lock Braking System" in attributes["features"]
        assert "Electronic Stability Control" in attributes["features"]
        
        assert "colors" in attributes
        assert "Crystal Black Pearl" in attributes["colors"]
        assert "Platinum White Pearl" in attributes["colors"]
    
    def test_format_response_removes_none_values(self, autodev_client):
        """Test that formatting removes None values."""
        # Arrange
        response_with_none = {
            "vin": "1HGBH41JXMN109186",
            "make": {"name": "Honda"},
            "model": None,
            "engine": {
                "name": "1.5L I4",
                "cylinder": None,
                "horsepower": 180
            }
        }
        
        # Act
        result = autodev_client.format_response(response_with_none)
        
        # Assert
        attributes = result["attributes"]
        assert "model" not in attributes  # None value should be removed
        assert attributes["engine"] == "1.5L I4"
        assert "cylinders" not in attributes  # None value should be removed
        assert attributes["horsepower"] == 180
    
    def test_validate_api_key_valid(self, autodev_client):
        """Test API key validation with valid keys."""
        # Arrange
        valid_keys = [
            "dGVzdF9hcGlfa2V5XzEyMzQ1",  # Base64-like
            "YWJjZGVmZ2hpams1234567890==",
            "VGVzdF9BUElfa2V5X3dpdGhfbG9uZ2VyX3N0cmluZw=="
        ]
        
        # Act & Assert
        for key in valid_keys:
            assert autodev_client.validate_api_key(key) is True
    
    def test_validate_api_key_invalid(self, autodev_client):
        """Test API key validation with invalid keys."""
        # Arrange
        invalid_keys = [
            "",               # Empty
            "short",          # Too short
            "invalid!@#$",    # Invalid characters
            None,            # None
            "123",           # Too short and only numbers
        ]
        
        # Act & Assert
        for key in invalid_keys:
            assert autodev_client.validate_api_key(key) is False
    
    @patch('httpx.AsyncClient')
    async def test_test_connection_success(
        self,
        mock_async_client,
        autodev_client
    ):
        """Test successful connection test."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status_code = 200
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act
        result = await autodev_client.test_connection()
        
        # Assert
        assert result is True
    
    @patch('httpx.AsyncClient')
    async def test_test_connection_not_found_but_api_works(
        self,
        mock_async_client,
        autodev_client
    ):
        """Test connection test with 404 (API works but test VIN not found)."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act
        result = await autodev_client.test_connection()
        
        # Assert
        assert result is True  # 404 means API works, just VIN not found
    
    @patch('httpx.AsyncClient')
    async def test_test_connection_unauthorized(
        self,
        mock_async_client,
        autodev_client
    ):
        """Test connection test with unauthorized response."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status_code = 401
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act
        result = await autodev_client.test_connection()
        
        # Assert
        assert result is False
    
    @patch('httpx.AsyncClient')
    async def test_test_connection_exception(
        self,
        mock_async_client,
        autodev_client
    ):
        """Test connection test with exception."""
        # Arrange
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = Exception("Connection error")
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Act
        result = await autodev_client.test_connection()
        
        # Assert
        assert result is False

