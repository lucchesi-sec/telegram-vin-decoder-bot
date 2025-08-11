"""Unit tests for DecodeVINHandler."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.application.vehicle.commands.handlers.decode_vin_handler import DecodeVINHandler, ApplicationException
from src.application.vehicle.commands import DecodeVINCommand
from src.domain.vehicle.value_objects.vin_number import VINNumber
from src.domain.vehicle.value_objects.decode_result import DecodeResult
from src.domain.vehicle.entities.vehicle import Vehicle
from src.domain.vehicle.events import VehicleDecodedEvent, DecodeFailedEvent


@pytest.mark.unit
@pytest.mark.application
class TestDecodeVINHandler:
    """Test cases for DecodeVINHandler."""
    
    @pytest.fixture
    def mock_vehicle_repo(self):
        """Mock vehicle repository."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_decoder_factory(self):
        """Mock decoder factory."""
        return MagicMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_logger(self):
        """Mock logger."""
        return MagicMock()
    
    @pytest.fixture
    def decode_vin_handler(self, mock_vehicle_repo, mock_decoder_factory, mock_event_bus, mock_logger):
        """Create DecodeVINHandler instance with mocked dependencies."""
        return DecodeVINHandler(
            vehicle_repo=mock_vehicle_repo,
            decoder_factory=mock_decoder_factory,
            event_bus=mock_event_bus,
            logger=mock_logger
        )
    
    @pytest.fixture
    def sample_command(self, sample_vin, sample_user_preferences):
        """Create a sample DecodeVINCommand."""
        return DecodeVINCommand(
            vin=sample_vin,
            user_preferences=sample_user_preferences,
            force_refresh=False
        )
    
    async def test_handle_decode_vin_cache_hit(
        self,
        decode_vin_handler,
        sample_command,
        sample_vehicle,
        mock_vehicle_repo,
        mock_decoder_factory,
        mock_event_bus
    ):
        """Test handling VIN decode with cache hit."""
        # Arrange
        mock_vehicle_repo.find_by_vin.return_value = sample_vehicle
        
        # Act
        result = await decode_vin_handler.handle(sample_command)
        
        # Assert
        assert isinstance(result, DecodeResult)
        assert result.vin == sample_vehicle.vin
        assert result.success is True
        
        # Verify repository was called but decoder was not
        mock_vehicle_repo.find_by_vin.assert_called_once_with(sample_command.vin)
        mock_decoder_factory.get_decoder.assert_not_called()
        mock_event_bus.publish.assert_not_called()
    
    async def test_handle_decode_vin_cache_miss(
        self,
        decode_vin_handler,
        sample_command,
        sample_vin,
        mock_vehicle_repo,
        mock_decoder_factory,
        mock_event_bus
    ):
        """Test handling VIN decode with cache miss."""
        # Arrange
        mock_vehicle_repo.find_by_vin.return_value = None
        
        mock_decoder = AsyncMock()
        mock_decoder.service_name = "nhtsa"
        mock_decoder.decode.return_value = {
            "manufacturer": "Honda",
            "model": "Civic",
            "year": 2021,
            "make": "Honda",
            "service": "nhtsa"
        }
        mock_decoder_factory.get_decoder.return_value = mock_decoder
        
        # Act
        result = await decode_vin_handler.handle(sample_command)
        
        # Assert
        assert isinstance(result, DecodeResult)
        assert result.success is True
        
        # Verify decoder was called
        mock_decoder_factory.get_decoder.assert_called_once_with(sample_command.user_preferences)
        mock_decoder.decode.assert_called_once_with(sample_command.vin)
        
        # Verify vehicle was saved
        mock_vehicle_repo.save.assert_called_once()
        
        # Verify events were published
        mock_event_bus.publish.assert_called()
    
    async def test_handle_decode_vin_force_refresh(
        self,
        decode_vin_handler,
        sample_vin,
        sample_user_preferences,
        sample_vehicle,
        mock_vehicle_repo,
        mock_decoder_factory,
        mock_event_bus
    ):
        """Test handling VIN decode with force refresh."""
        # Arrange
        command = DecodeVINCommand(
            vin=sample_vin,
            user_preferences=sample_user_preferences,
            force_refresh=True
        )
        
        mock_vehicle_repo.find_by_vin.return_value = sample_vehicle
        
        mock_decoder = AsyncMock()
        mock_decoder.service_name = "nhtsa"
        mock_decoder.decode.return_value = {
            "manufacturer": "Honda",
            "model": "Civic",
            "year": 2021,
            "make": "Honda",
            "service": "nhtsa"
        }
        mock_decoder_factory.get_decoder.return_value = mock_decoder
        
        # Act
        result = await decode_vin_handler.handle(command)
        
        # Assert
        assert isinstance(result, DecodeResult)
        assert result.success is True
        
        # Verify decoder was called even though cached vehicle exists
        mock_decoder_factory.get_decoder.assert_called_once()
        mock_decoder.decode.assert_called_once()
    
    async def test_handle_decode_vin_decoder_failure(
        self,
        decode_vin_handler,
        sample_command,
        mock_vehicle_repo,
        mock_decoder_factory,
        mock_event_bus
    ):
        """Test handling VIN decode when decoder fails."""
        # Arrange
        mock_vehicle_repo.find_by_vin.return_value = None
        
        mock_decoder = AsyncMock()
        mock_decoder.service_name = "nhtsa"
        mock_decoder.decode.side_effect = Exception("API rate limit exceeded")
        mock_decoder_factory.get_decoder.return_value = mock_decoder
        
        # Act & Assert
        with pytest.raises(ApplicationException) as exc_info:
            await decode_vin_handler.handle(sample_command)
        
        assert "Unable to decode VIN" in str(exc_info.value)
        
        # Verify decode failed event was published
        mock_event_bus.publish.assert_called()
        published_event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(published_event, DecodeFailedEvent)
        assert published_event.vin == sample_command.vin.value
        assert published_event.service_used == "nhtsa"
        assert "API rate limit exceeded" in published_event.error_message
    
    async def test_handle_decode_vin_repository_failure(
        self,
        decode_vin_handler,
        sample_command,
        mock_vehicle_repo,
        mock_decoder_factory
    ):
        """Test handling VIN decode when repository fails."""
        # Arrange
        mock_vehicle_repo.find_by_vin.side_effect = Exception("Database connection error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await decode_vin_handler.handle(sample_command)
        
        assert "Database connection error" in str(exc_info.value)
        
        # Verify decoder was not called
        mock_decoder_factory.get_decoder.assert_not_called()
    
    def test_create_vehicle_from_result(self, decode_vin_handler, sample_vin):
        """Test creating vehicle from decode result."""
        # Arrange
        raw_result = {
            "manufacturer": "Honda",
            "model": "Civic",
            "year": 2021,
            "make": "Honda",
            "body_type": "Sedan",
            "service": "nhtsa"
        }
        
        # Act
        vehicle = decode_vin_handler._create_vehicle_from_result(sample_vin, raw_result)
        
        # Assert
        assert isinstance(vehicle, Vehicle)
        assert vehicle.vin == sample_vin
        assert vehicle.manufacturer == "Honda"
        assert vehicle.model == "Civic"
        assert vehicle.model_year.value == 2021
        assert vehicle.attributes == raw_result
        assert len(vehicle.decode_history) == 1
        assert vehicle.decode_history[0].service_used == "nhtsa"
    
    def test_create_vehicle_from_result_missing_fields(self, decode_vin_handler, sample_vin):
        """Test creating vehicle from decode result with missing fields."""
        # Arrange
        raw_result = {
            "make": "Honda"
            # Missing manufacturer, model, year
        }
        
        # Act
        vehicle = decode_vin_handler._create_vehicle_from_result(sample_vin, raw_result)
        
        # Assert
        assert vehicle.manufacturer == "Unknown"
        assert vehicle.model == "Unknown"
        assert vehicle.model_year.value == 2020  # Default year
        assert vehicle.attributes == raw_result
    
    def test_vehicle_to_decode_result(self, decode_vin_handler, sample_vehicle):
        """Test converting vehicle to decode result."""
        # Act
        result = decode_vin_handler._vehicle_to_decode_result(sample_vehicle)
        
        # Assert
        assert isinstance(result, DecodeResult)
        assert result.vin == sample_vehicle.vin
        assert result.success is True
        assert result.data == sample_vehicle.attributes
        assert result.service_used == "Unknown"  # Since we don't have decode attempt history
    
    async def test_handle_publishes_domain_events(
        self,
        decode_vin_handler,
        sample_command,
        mock_vehicle_repo,
        mock_decoder_factory,
        mock_event_bus
    ):
        """Test that handling publishes domain events from vehicle."""
        # Arrange
        mock_vehicle_repo.find_by_vin.return_value = None
        
        mock_decoder = AsyncMock()
        mock_decoder.service_name = "nhtsa"
        mock_decoder.decode.return_value = {
            "manufacturer": "Honda",
            "model": "Civic",
            "year": 2021,
            "service": "nhtsa"
        }
        mock_decoder_factory.get_decoder.return_value = mock_decoder
        
        # Act
        await decode_vin_handler.handle(sample_command)
        
        # Assert
        # Should publish events from the created vehicle
        assert mock_event_bus.publish.call_count >= 1
        
        # Get the first published event (should be VehicleDecodedEvent)
        first_call = mock_event_bus.publish.call_args_list[0]
        published_event = first_call[0][0]
        assert isinstance(published_event, VehicleDecodedEvent)
        assert published_event.vin == sample_command.vin.value
    
    def test_application_exception_creation(self):
        """Test ApplicationException creation."""
        # Arrange
        message = "Test error message"
        cause = Exception("Root cause")
        
        # Act
        exception = ApplicationException(message, cause)
        
        # Assert
        assert str(exception) == message
        assert exception.cause == cause
    
    def test_application_exception_without_cause(self):
        """Test ApplicationException creation without cause."""
        # Arrange
        message = "Test error message"
        
        # Act
        exception = ApplicationException(message)
        
        # Assert
        assert str(exception) == message
        assert exception.cause is None
    
    async def test_decode_vin_handler_logging(
        self,
        decode_vin_handler,
        sample_command,
        mock_vehicle_repo,
        mock_decoder_factory,
        mock_event_bus,
        mock_logger
    ):
        """Test that handler logs appropriately."""
        # Arrange
        mock_vehicle_repo.find_by_vin.return_value = None
        
        mock_decoder = AsyncMock()
        mock_decoder.service_name = "nhtsa"
        mock_decoder.decode.side_effect = Exception("API error")
        mock_decoder_factory.get_decoder.return_value = mock_decoder
        
        # Act
        with pytest.raises(ApplicationException):
            await decode_vin_handler.handle(sample_command)
        
        # Assert
        mock_logger.error.assert_called()
        error_calls = [call for call in mock_logger.error.call_args_list]
        assert len(error_calls) >= 1
        
        # Check that the error message contains relevant information
        error_message = error_calls[0][0][0]
        assert "Decoding failed for VIN" in error_message
        assert sample_command.vin.value in error_message
