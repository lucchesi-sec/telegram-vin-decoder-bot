"""Integration tests for vehicle decode flow."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.config.dependencies import Container
from src.application.vehicle.commands import DecodeVINCommand
from src.application.vehicle.commands.handlers.decode_vin_handler import DecodeVINHandler
from src.domain.vehicle.value_objects.vin_number import VINNumber
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.domain.vehicle.entities.vehicle import Vehicle
from src.domain.vehicle.events import VehicleDecodedEvent


@pytest.mark.integration
@pytest.mark.external
class TestVehicleDecodeFlow:
    """Integration tests for the vehicle decode flow."""
    
    @pytest.fixture
    def container(self, mock_settings):
        """Create a test container with mocked external dependencies."""
        container = Container()
        container.config.from_dict({
            'telegram': mock_settings.telegram.model_dump(),
            'decoder': mock_settings.decoder.model_dump(),
            'cache': mock_settings.cache.model_dump()
        })
        return container
    
    async def test_end_to_end_decode_flow_with_nhtsa(
        self,
        container,
        sample_vin,
        sample_user_preferences,
        mock_nhtsa_response
    ):
        """Test complete decode flow using NHTSA service."""
        # Arrange
        preferences = UserPreferences(preferred_decoder="nhtsa")
        command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=preferences,
            force_refresh=False
        )
        
        # Mock NHTSA client response
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_nhtsa_response
            mock_response.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Get handler from container
            handler = container.decode_vin_handler()
            
            # Act
            result = await handler.handle(command)
            
            # Assert
            assert result.success is True
            assert result.vin == sample_vin
            assert "Honda" in str(result.data)
            assert "Civic" in str(result.data)
    
    async def test_end_to_end_decode_flow_with_autodev(
        self,
        container,
        sample_vin,
        sample_user_preferences,
        mock_autodev_response
    ):
        """Test complete decode flow using AutoDev service."""
        # Arrange
        preferences = UserPreferences(preferred_decoder="autodev")
        command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=preferences,
            force_refresh=False
        )
        
        # Mock AutoDev client response
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_autodev_response
            mock_response.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Get handler from container
            handler = container.decode_vin_handler()
            
            # Act
            result = await handler.handle(command)
            
            # Assert
            assert result.success is True
            assert result.vin == sample_vin
            assert "Honda" in str(result.data)
            assert "Civic" in str(result.data)
    
    async def test_decode_flow_with_caching(
        self,
        container,
        sample_vin,
        sample_user_preferences
    ):
        """Test decode flow with caching behavior."""
        # Arrange
        command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=sample_user_preferences,
            force_refresh=False
        )
        
        # Get repositories
        vehicle_repo = container.vehicle_repository()
        
        # Pre-populate cache with a vehicle
        cached_vehicle = Vehicle.create_from_decode_result(
            vin=sample_vin,
            manufacturer="Honda",
            model="Civic",
            model_year=ModelYear(2021),
            attributes={"make": "Honda", "model": "Civic", "year": 2021},
            service_used="nhtsa"
        )
        await vehicle_repo.save(cached_vehicle)
        
        # Get handler
        handler = container.decode_vin_handler()
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.vin == sample_vin
        # Should return cached data without hitting external API
        assert result.data == cached_vehicle.attributes
    
    async def test_decode_flow_force_refresh_bypasses_cache(
        self,
        container,
        sample_vin,
        sample_user_preferences,
        mock_nhtsa_response
    ):
        """Test that force refresh bypasses cache."""
        # Arrange
        command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=sample_user_preferences,
            force_refresh=True
        )
        
        # Get repositories
        vehicle_repo = container.vehicle_repository()
        
        # Pre-populate cache with a vehicle
        cached_vehicle = Vehicle.create_from_decode_result(
            vin=sample_vin,
            manufacturer="Toyota",  # Different from mock response
            model="Camry",
            model_year=ModelYear(2020),
            attributes={"make": "Toyota", "model": "Camry", "year": 2020},
            service_used="nhtsa"
        )
        await vehicle_repo.save(cached_vehicle)
        
        # Mock external API call
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_nhtsa_response
            mock_response.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Get handler
            handler = container.decode_vin_handler()
            
            # Act
            result = await handler.handle(command)
            
            # Assert
            assert result.success is True
            # Should have fresh data from API, not cached data
            assert "Honda" in str(result.data)  # From mock response
            assert "Toyota" not in str(result.data)  # Not from cache
    
    async def test_decode_flow_event_publishing(
        self,
        container,
        sample_vin,
        sample_user_preferences,
        mock_nhtsa_response
    ):
        """Test that decode flow publishes domain events."""
        # Arrange
        command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=sample_user_preferences,
            force_refresh=False
        )
        
        # Mock external API call
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_nhtsa_response
            mock_response.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Get handler and mock event bus
            handler = container.decode_vin_handler()
            mock_event_bus = AsyncMock()
            handler.event_bus = mock_event_bus
            
            # Act
            result = await handler.handle(command)
            
            # Assert
            assert result.success is True
            
            # Verify events were published
            mock_event_bus.publish.assert_called()
            
            # Check that VehicleDecodedEvent was published
            published_events = [call[0][0] for call in mock_event_bus.publish.call_args_list]
            vehicle_decoded_events = [e for e in published_events if isinstance(e, VehicleDecodedEvent)]
            assert len(vehicle_decoded_events) == 1
            
            event = vehicle_decoded_events[0]
            assert event.vin == sample_vin.value
            assert isinstance(event.decoded_at, datetime)
    
    async def test_decode_flow_error_handling_and_fallback(
        self,
        container,
        sample_vin,
        sample_user_preferences
    ):
        """Test decode flow error handling and fallback mechanisms."""
        # Arrange
        command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=sample_user_preferences,
            force_refresh=False
        )
        
        # Mock external API to fail
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get.side_effect = Exception("API unavailable")
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Get handler
            handler = container.decode_vin_handler()
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                await handler.handle(command)
            
            assert "Unable to decode VIN" in str(exc_info.value)
    
    async def test_decode_flow_with_repository_persistence(
        self,
        container,
        sample_vin,
        sample_user_preferences,
        mock_nhtsa_response
    ):
        """Test that decoded vehicles are properly persisted."""
        # Arrange
        command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=sample_user_preferences,
            force_refresh=False
        )
        
        # Mock external API call
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_nhtsa_response
            mock_response.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Get handler and repository
            handler = container.decode_vin_handler()
            vehicle_repo = container.vehicle_repository()
            
            # Act
            result = await handler.handle(command)
            
            # Assert
            assert result.success is True
            
            # Verify vehicle was saved to repository
            saved_vehicle = await vehicle_repo.find_by_vin(sample_vin)
            assert saved_vehicle is not None
            assert saved_vehicle.vin == sample_vin
            assert saved_vehicle.manufacturer == "Honda"
            assert saved_vehicle.model == "Civic"
            assert len(saved_vehicle.decode_history) >= 1
    
    async def test_decode_flow_decoder_factory_selection(
        self,
        container,
        sample_vin,
        mock_nhtsa_response,
        mock_autodev_response
    ):
        """Test that decoder factory selects correct service based on preferences."""
        # Test NHTSA selection
        nhtsa_preferences = UserPreferences(preferred_decoder="nhtsa")
        nhtsa_command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=nhtsa_preferences,
            force_refresh=False
        )
        
        # Mock NHTSA response
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_nhtsa_response
            mock_response.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            handler = container.decode_vin_handler()
            
            # Act
            nhtsa_result = await handler.handle(nhtsa_command)
            
            # Assert
            assert nhtsa_result.success is True
            # NHTSA URL should have been called
            called_url = mock_client_instance.get.call_args[0][0]
            assert "vpic.nhtsa.dot.gov" in called_url
        
        # Test AutoDev selection
        autodev_preferences = UserPreferences(preferred_decoder="autodev")
        autodev_command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=autodev_preferences,
            force_refresh=True  # Force refresh to bypass any cache
        )
        
        # Mock AutoDev response
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_autodev_response
            mock_response.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Act
            autodev_result = await handler.handle(autodev_command)
            
            # Assert
            assert autodev_result.success is True
            # AutoDev URL should have been called
            called_url = mock_client_instance.get.call_args[0][0]
            assert "auto.dev" in called_url

