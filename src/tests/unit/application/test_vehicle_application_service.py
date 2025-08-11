"""Unit tests for Vehicle Application Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.application.vehicle.services.vehicle_application_service import VehicleApplicationService
from src.domain.vehicle.value_objects.vin_number import VINNumber
from src.domain.vehicle.value_objects.decode_result import DecodeResult
from src.domain.vehicle.entities.vehicle import Vehicle
from src.tests.utils.factories import VINFactory, VehicleFactory, APIResponseFactory
from src.tests.utils.helpers import AsyncTestCase


class TestVehicleApplicationService:
    """Test VehicleApplicationService."""
    
    @pytest.fixture
    def mock_vehicle_repository(self):
        """Create mock vehicle repository."""
        repo = AsyncMock()
        repo.find_by_vin = AsyncMock(return_value=None)
        repo.save = AsyncMock()
        repo.find_recent = AsyncMock(return_value=[])
        repo.find_by_user = AsyncMock(return_value=[])
        repo.count_by_user = AsyncMock(return_value=0)
        return repo
    
    @pytest.fixture
    def mock_decoder_factory(self):
        """Create mock decoder factory."""
        factory = MagicMock()
        mock_decoder = AsyncMock()
        mock_decoder.decode_vin = AsyncMock(return_value=DecodeResult(
            success=True,
            vin="1HGBH41JXMN109186",
            manufacturer="Honda",
            model="Civic",
            model_year=2021,
            attributes={"engine": "1.5L"},
            service_used="nhtsa"
        ))
        factory.get_decoder = MagicMock(return_value=mock_decoder)
        return factory
    
    @pytest.fixture
    def mock_cache_repository(self):
        """Create mock cache repository."""
        cache = AsyncMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock(return_value=True)
        cache.delete = AsyncMock(return_value=True)
        return cache
    
    @pytest.fixture
    def mock_event_bus(self):
        """Create mock event bus."""
        bus = AsyncMock()
        bus.publish = AsyncMock()
        return bus
    
    @pytest.fixture
    def vehicle_service(
        self,
        mock_vehicle_repository,
        mock_decoder_factory,
        mock_cache_repository,
        mock_event_bus
    ):
        """Create VehicleApplicationService instance."""
        return VehicleApplicationService(
            vehicle_repository=mock_vehicle_repository,
            decoder_factory=mock_decoder_factory,
            cache_repository=mock_cache_repository,
            event_bus=mock_event_bus
        )
    
    @pytest.mark.asyncio
    async def test_decode_vin_success(self, vehicle_service, mock_decoder_factory):
        """Test successful VIN decoding."""
        vin = "1HGBH41JXMN109186"
        user_id = 123456789
        
        result = await vehicle_service.decode_vin(
            vin=vin,
            user_id=user_id,
            decoder_service="nhtsa"
        )
        
        assert result.success is True
        assert result.vin == vin
        assert result.manufacturer == "Honda"
        assert result.model == "Civic"
        mock_decoder_factory.get_decoder.assert_called_once_with("nhtsa")
    
    @pytest.mark.asyncio
    async def test_decode_vin_with_cache_hit(
        self,
        vehicle_service,
        mock_cache_repository,
        mock_decoder_factory
    ):
        """Test VIN decoding with cache hit."""
        vin = "1HGBH41JXMN109186"
        cached_result = DecodeResult(
            success=True,
            vin=vin,
            manufacturer="Honda",
            model="Civic", 
            model_year=2021,
            service_used="nhtsa"
        )
        
        mock_cache_repository.get.return_value = cached_result.to_dict()
        
        result = await vehicle_service.decode_vin(
            vin=vin,
            user_id=123456789,
            decoder_service="nhtsa"
        )
        
        assert result.success is True
        assert result.vin == vin
        mock_decoder_factory.get_decoder.assert_not_called()
        mock_cache_repository.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_decode_vin_invalid_format(self, vehicle_service):
        """Test decoding with invalid VIN format."""
        invalid_vin = "INVALID123"
        
        result = await vehicle_service.decode_vin(
            vin=invalid_vin,
            user_id=123456789,
            decoder_service="nhtsa"
        )
        
        assert result.success is False
        assert "Invalid VIN format" in result.error_message
    
    @pytest.mark.asyncio
    async def test_decode_vin_decoder_failure(
        self,
        vehicle_service,
        mock_decoder_factory
    ):
        """Test handling decoder service failure."""
        mock_decoder = AsyncMock()
        mock_decoder.decode_vin = AsyncMock(side_effect=Exception("API Error"))
        mock_decoder_factory.get_decoder.return_value = mock_decoder
        
        result = await vehicle_service.decode_vin(
            vin="1HGBH41JXMN109186",
            user_id=123456789,
            decoder_service="nhtsa"
        )
        
        assert result.success is False
        assert "Failed to decode VIN" in result.error_message
    
    @pytest.mark.asyncio
    async def test_save_decoded_vehicle(
        self,
        vehicle_service,
        mock_vehicle_repository
    ):
        """Test saving decoded vehicle to repository."""
        vin = "1HGBH41JXMN109186"
        user_id = 123456789
        
        result = await vehicle_service.decode_vin(
            vin=vin,
            user_id=user_id,
            decoder_service="nhtsa",
            save_to_history=True
        )
        
        assert result.success is True
        mock_vehicle_repository.save.assert_called_once()
        saved_vehicle = mock_vehicle_repository.save.call_args[0][0]
        assert isinstance(saved_vehicle, Vehicle)
        assert saved_vehicle.vin.value == vin
    
    @pytest.mark.asyncio
    async def test_get_recent_vehicles(
        self,
        vehicle_service,
        mock_vehicle_repository
    ):
        """Test getting recent vehicles for user."""
        user_id = 123456789
        vehicles = [
            VehicleFactory.create_vehicle() for _ in range(3)
        ]
        mock_vehicle_repository.find_recent.return_value = vehicles
        
        result = await vehicle_service.get_recent_vehicles(
            user_id=user_id,
            limit=10
        )
        
        assert len(result) == 3
        mock_vehicle_repository.find_recent.assert_called_once_with(
            user_id=user_id,
            limit=10
        )
    
    @pytest.mark.asyncio
    async def test_get_vehicle_by_vin(
        self,
        vehicle_service,
        mock_vehicle_repository
    ):
        """Test getting vehicle by VIN."""
        vin = "1HGBH41JXMN109186"
        vehicle = VehicleFactory.create_vehicle(vin=vin)
        mock_vehicle_repository.find_by_vin.return_value = vehicle
        
        result = await vehicle_service.get_vehicle_by_vin(vin)
        
        assert result is not None
        assert result.vin.value == vin
        mock_vehicle_repository.find_by_vin.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_decode_vin_with_fallback_service(
        self,
        vehicle_service,
        mock_decoder_factory
    ):
        """Test fallback to alternative decoder service on failure."""
        vin = "1HGBH41JXMN109186"
        
        # First decoder fails
        failing_decoder = AsyncMock()
        failing_decoder.decode_vin = AsyncMock(side_effect=Exception("API Error"))
        
        # Fallback decoder succeeds
        fallback_decoder = AsyncMock()
        fallback_decoder.decode_vin = AsyncMock(return_value=DecodeResult(
            success=True,
            vin=vin,
            manufacturer="Honda",
            model="Civic",
            model_year=2021,
            service_used="autodev"
        ))
        
        mock_decoder_factory.get_decoder.side_effect = [
            failing_decoder,
            fallback_decoder
        ]
        
        result = await vehicle_service.decode_vin(
            vin=vin,
            user_id=123456789,
            decoder_service="nhtsa",
            fallback_service="autodev"
        )
        
        assert result.success is True
        assert result.service_used == "autodev"
        assert mock_decoder_factory.get_decoder.call_count == 2
    
    @pytest.mark.asyncio
    async def test_batch_decode_vins(
        self,
        vehicle_service,
        mock_decoder_factory
    ):
        """Test batch VIN decoding."""
        vins = [VINFactory.create_valid_vin(i) for i in range(3)]
        user_id = 123456789
        
        results = await vehicle_service.batch_decode_vins(
            vins=vins,
            user_id=user_id,
            decoder_service="nhtsa"
        )
        
        assert len(results) == 3
        for result in results:
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_get_user_statistics(
        self,
        vehicle_service,
        mock_vehicle_repository
    ):
        """Test getting user vehicle statistics."""
        user_id = 123456789
        vehicles = [
            VehicleFactory.create_vehicle(manufacturer="Honda"),
            VehicleFactory.create_vehicle(manufacturer="Honda"),
            VehicleFactory.create_vehicle(manufacturer="Toyota"),
        ]
        mock_vehicle_repository.find_by_user.return_value = vehicles
        mock_vehicle_repository.count_by_user.return_value = 3
        
        stats = await vehicle_service.get_user_statistics(user_id)
        
        assert stats["total_vehicles"] == 3
        assert stats["unique_manufacturers"] == 2
        assert "Honda" in stats["manufacturer_counts"]
        assert stats["manufacturer_counts"]["Honda"] == 2
    
    @pytest.mark.asyncio
    async def test_clear_user_cache(
        self,
        vehicle_service,
        mock_cache_repository
    ):
        """Test clearing user's vehicle cache."""
        user_id = 123456789
        
        await vehicle_service.clear_user_cache(user_id)
        
        mock_cache_repository.delete.assert_called()
    
    @pytest.mark.asyncio
    async def test_validate_vin_format(self, vehicle_service):
        """Test VIN format validation."""
        valid_vins = [
            "1HGBH41JXMN109186",
            "WBANE53517C123456",
            "5YJSA1DN5DF123456",
        ]
        
        for vin in valid_vins:
            assert vehicle_service.validate_vin_format(vin) is True
        
        invalid_vins = [
            "INVALID",
            "12345",
            "",
            None,
            "1234567890ABCDEFGH",  # 18 chars
        ]
        
        for vin in invalid_vins:
            assert vehicle_service.validate_vin_format(vin) is False
    
    @pytest.mark.asyncio
    async def test_event_publishing_on_decode(
        self,
        vehicle_service,
        mock_event_bus
    ):
        """Test that events are published when vehicle is decoded."""
        vin = "1HGBH41JXMN109186"
        user_id = 123456789
        
        await vehicle_service.decode_vin(
            vin=vin,
            user_id=user_id,
            decoder_service="nhtsa"
        )
        
        mock_event_bus.publish.assert_called()
        published_event = mock_event_bus.publish.call_args[0][0]
        assert hasattr(published_event, 'vin')
        assert hasattr(published_event, 'user_id')