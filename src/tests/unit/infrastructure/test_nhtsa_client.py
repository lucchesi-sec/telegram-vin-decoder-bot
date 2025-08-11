"""Unit tests for NHTSA Client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.infrastructure.external_services.nhtsa.nhtsa_client import NHTSAClient
from src.domain.vehicle.value_objects.decode_result import DecodeResult
from src.tests.utils.factories import VINFactory, APIResponseFactory
from src.tests.utils.helpers import MockResponse, mock_httpx_client


class TestNHTSAClient:
    """Test NHTSA API Client."""
    
    @pytest.fixture
    def nhtsa_client(self):
        """Create NHTSA client instance."""
        return NHTSAClient(
            api_key="test_api_key",
            timeout=30
        )
    
    @pytest.mark.asyncio
    async def test_decode_vin_success(self, nhtsa_client):
        """Test successful VIN decoding."""
        vin = "1HGBH41JXMN109186"
        mock_response_data = APIResponseFactory.create_nhtsa_response(vin)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = MockResponse(
                status_code=200,
                json_data=mock_response_data
            )
            
            result = await nhtsa_client.decode_vin(vin)
            
            assert result.success is True
            assert result.vin == vin
            assert result.manufacturer == "Honda"
            assert result.model == "Civic"
            assert result.service_used == "nhtsa"
            
            mock_client.get.assert_called_once()
            call_url = mock_client.get.call_args[0][0]
            assert f"DecodeVin/{vin}" in call_url
    
    @pytest.mark.asyncio
    async def test_decode_vin_not_found(self, nhtsa_client):
        """Test VIN decoding when VIN is not found."""
        vin = "INVALID1234567890"
        mock_response_data = {
            "Count": 0,
            "Message": "No data found",
            "Results": []
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = MockResponse(
                status_code=200,
                json_data=mock_response_data
            )
            
            result = await nhtsa_client.decode_vin(vin)
            
            assert result.success is False
            assert "No data found" in result.error_message
    
    @pytest.mark.asyncio
    async def test_decode_vin_api_error(self, nhtsa_client):
        """Test handling API errors."""
        vin = "1HGBH41JXMN109186"
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = MockResponse(
                status_code=500,
                raise_on_status=True
            )
            
            result = await nhtsa_client.decode_vin(vin)
            
            assert result.success is False
            assert "API error" in result.error_message
    
    @pytest.mark.asyncio
    async def test_decode_vin_network_error(self, nhtsa_client):
        """Test handling network errors."""
        vin = "1HGBH41JXMN109186"
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.NetworkError("Connection failed")
            
            result = await nhtsa_client.decode_vin(vin)
            
            assert result.success is False
            assert "Network error" in result.error_message
    
    @pytest.mark.asyncio
    async def test_decode_vin_timeout(self, nhtsa_client):
        """Test handling timeout errors."""
        vin = "1HGBH41JXMN109186"
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
            
            result = await nhtsa_client.decode_vin(vin)
            
            assert result.success is False
            assert "timeout" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_parse_response_complete_data(self, nhtsa_client):
        """Test parsing complete NHTSA response."""
        response_data = {
            "Count": 1,
            "Results": [{
                "Make": "Honda",
                "Model": "Civic",
                "ModelYear": "2021",
                "VehicleType": "PASSENGER CAR",
                "BodyClass": "Sedan/Saloon",
                "EngineModel": "L15B7",
                "EngineCylinders": "4",
                "DisplacementL": "1.5",
                "FuelTypePrimary": "Gasoline",
                "TransmissionStyle": "CVT",
                "Doors": "4",
                "PlantCountry": "United States",
                "PlantState": "Ohio",
                "PlantCity": "Marysville"
            }]
        }
        
        result = nhtsa_client._parse_response(response_data, "1HGBH41JXMN109186")
        
        assert result.success is True
        assert result.manufacturer == "Honda"
        assert result.model == "Civic"
        assert result.model_year == 2021
        assert result.attributes["engine_cylinders"] == "4"
        assert result.attributes["fuel_type"] == "Gasoline"
        assert result.attributes["transmission"] == "CVT"
        assert result.attributes["doors"] == "4"
    
    @pytest.mark.asyncio
    async def test_parse_response_partial_data(self, nhtsa_client):
        """Test parsing partial NHTSA response."""
        response_data = {
            "Count": 1,
            "Results": [{
                "Make": "Honda",
                "Model": "Civic",
                "ModelYear": "2021",
                "VehicleType": "",
                "BodyClass": None,
                "EngineModel": "",
                "EngineCylinders": "",
                "DisplacementL": "",
            }]
        }
        
        result = nhtsa_client._parse_response(response_data, "1HGBH41JXMN109186")
        
        assert result.success is True
        assert result.manufacturer == "Honda"
        assert result.model == "Civic"
        assert result.model_year == 2021
        assert "engine_cylinders" not in result.attributes
    
    @pytest.mark.asyncio
    async def test_get_recalls(self, nhtsa_client):
        """Test getting vehicle recalls."""
        vin = "1HGBH41JXMN109186"
        mock_recalls = {
            "Count": 2,
            "Results": [
                {
                    "Component": "AIRBAGS",
                    "Summary": "Airbag may not deploy properly",
                    "Consequence": "Increased risk of injury",
                    "Remedy": "Replace airbag module",
                    "NHTSACampaignNumber": "21V123000"
                },
                {
                    "Component": "ENGINE",
                    "Summary": "Engine may stall",
                    "Consequence": "Loss of power",
                    "Remedy": "Software update",
                    "NHTSACampaignNumber": "21V456000"
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = MockResponse(
                status_code=200,
                json_data=mock_recalls
            )
            
            recalls = await nhtsa_client.get_recalls(vin)
            
            assert len(recalls) == 2
            assert recalls[0]["component"] == "AIRBAGS"
            assert recalls[0]["campaign_number"] == "21V123000"
            assert recalls[1]["component"] == "ENGINE"
    
    @pytest.mark.asyncio
    async def test_get_safety_ratings(self, nhtsa_client):
        """Test getting vehicle safety ratings."""
        vin = "1HGBH41JXMN109186"
        mock_ratings = {
            "Count": 1,
            "Results": [{
                "OverallRating": "5",
                "OverallFrontCrashRating": "5",
                "FrontCrashDriversideRating": "5",
                "FrontCrashPassengersideRating": "5",
                "OverallSideCrashRating": "5",
                "RolloverRating": "4",
                "RolloverPossibility": "12.5",
                "ComplaintsCount": "15"
            }]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = MockResponse(
                status_code=200,
                json_data=mock_ratings
            )
            
            ratings = await nhtsa_client.get_safety_ratings(vin)
            
            assert ratings["overall_rating"] == "5"
            assert ratings["front_crash_rating"] == "5"
            assert ratings["side_crash_rating"] == "5"
            assert ratings["rollover_rating"] == "4"
            assert ratings["rollover_possibility"] == "12.5"
    
    @pytest.mark.asyncio
    async def test_batch_decode_vins(self, nhtsa_client):
        """Test batch VIN decoding."""
        vins = [VINFactory.create_valid_vin(i) for i in range(3)]
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            responses = [
                MockResponse(
                    status_code=200,
                    json_data=APIResponseFactory.create_nhtsa_response(vin)
                ) for vin in vins
            ]
            mock_client.get.side_effect = responses
            
            results = await nhtsa_client.batch_decode_vins(vins)
            
            assert len(results) == 3
            for i, result in enumerate(results):
                assert result.success is True
                assert result.vin == vins[i]
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self, nhtsa_client):
        """Test retry mechanism on API failure."""
        vin = "1HGBH41JXMN109186"
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # First call fails, second succeeds
            mock_client.get.side_effect = [
                MockResponse(status_code=503, raise_on_status=True),
                MockResponse(
                    status_code=200,
                    json_data=APIResponseFactory.create_nhtsa_response(vin)
                )
            ]
            
            result = await nhtsa_client.decode_vin(vin, retry_count=1)
            
            assert result.success is True
            assert mock_client.get.call_count == 2
    
    @pytest.mark.asyncio
    async def test_cache_integration(self, nhtsa_client):
        """Test cache integration with NHTSA client."""
        vin = "1HGBH41JXMN109186"
        mock_cache = AsyncMock()
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        
        nhtsa_client.cache = mock_cache
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = MockResponse(
                status_code=200,
                json_data=APIResponseFactory.create_nhtsa_response(vin)
            )
            
            result = await nhtsa_client.decode_vin(vin)
            
            assert result.success is True
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once()
    
    def test_build_url(self, nhtsa_client):
        """Test URL building for different endpoints."""
        base_url = "https://vpic.nhtsa.dot.gov/api/vehicles"
        
        # Test VIN decode URL
        vin = "1HGBH41JXMN109186"
        url = nhtsa_client._build_url(f"DecodeVin/{vin}")
        assert url == f"{base_url}/DecodeVin/{vin}?format=json"
        
        # Test recalls URL
        url = nhtsa_client._build_url(f"Recalls/vehicle/vin/{vin}")
        assert url == f"{base_url}/Recalls/vehicle/vin/{vin}?format=json"
    
    def test_sanitize_vin(self, nhtsa_client):
        """Test VIN sanitization."""
        test_cases = [
            ("1HGBH41JXMN109186", "1HGBH41JXMN109186"),
            ("  1HGBH41JXMN109186  ", "1HGBH41JXMN109186"),
            ("1hgbh41jxmn109186", "1HGBH41JXMN109186"),
            ("1HG-BH41-JXMN-109186", "1HGBH41JXMN109186"),
        ]
        
        for input_vin, expected in test_cases:
            assert nhtsa_client._sanitize_vin(input_vin) == expected