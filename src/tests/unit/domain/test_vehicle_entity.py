"""Unit tests for Vehicle domain entity."""

import pytest
from datetime import datetime
from src.domain.vehicle.entities.vehicle import Vehicle, DecodeAttempt
from src.domain.vehicle.value_objects.vin_number import VINNumber
from src.domain.vehicle.value_objects.model_year import ModelYear
from src.domain.vehicle.events import VehicleDecodedEvent


@pytest.mark.unit
@pytest.mark.domain
class TestVehicleEntity:
    """Test cases for Vehicle domain entity."""
    
    def test_vehicle_creation_from_decode_result(self, sample_vin):
        """Test vehicle creation from decode result."""
        # Arrange
        manufacturer = "Honda"
        model = "Civic"
        model_year = ModelYear(2021)
        attributes = {
            "make": "Honda",
            "model": "Civic",
            "year": 2021,
            "body_type": "Sedan"
        }
        service_used = "nhtsa"
        
        # Act
        vehicle = Vehicle.create_from_decode_result(
            vin=sample_vin,
            manufacturer=manufacturer,
            model=model,
            model_year=model_year,
            attributes=attributes,
            service_used=service_used
        )
        
        # Assert
        assert vehicle.vin == sample_vin
        assert vehicle.manufacturer == manufacturer
        assert vehicle.model == model
        assert vehicle.model_year == model_year
        assert vehicle.attributes == attributes
        assert len(vehicle.decode_history) == 1
        
        # Check decode attempt
        decode_attempt = vehicle.decode_history[0]
        assert isinstance(decode_attempt, DecodeAttempt)
        assert decode_attempt.service_used == service_used
        assert decode_attempt.success is True
        assert decode_attempt.error_message is None
        assert isinstance(decode_attempt.timestamp, datetime)
        
        # Check domain events
        events = vehicle.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], VehicleDecodedEvent)
        assert events[0].aggregate_id == vehicle.id
        assert events[0].vin == sample_vin.value
    
    def test_vehicle_direct_instantiation(self, sample_vin):
        """Test direct vehicle instantiation."""
        # Arrange
        model_year = ModelYear(2021)
        attributes = {"make": "Honda", "model": "Civic"}
        
        # Act
        vehicle = Vehicle(
            vin=sample_vin,
            manufacturer="Honda",
            model="Civic",
            model_year=model_year,
            attributes=attributes
        )
        
        # Assert
        assert vehicle.vin == sample_vin
        assert vehicle.manufacturer == "Honda"
        assert vehicle.model == "Civic"
        assert vehicle.model_year == model_year
        assert vehicle.attributes == attributes
        assert len(vehicle.decode_history) == 0
    
    def test_update_attributes(self, sample_vehicle):
        """Test updating vehicle attributes."""
        # Arrange
        new_attributes = {
            "color": "Blue",
            "trim": "EX-L"
        }
        original_attributes = sample_vehicle.attributes.copy()
        
        # Act
        sample_vehicle.update_attributes(new_attributes)
        
        # Assert
        expected_attributes = {**original_attributes, **new_attributes}
        assert sample_vehicle.attributes == expected_attributes
        assert sample_vehicle.updated_at is not None
    
    def test_add_decode_attempt_success(self, sample_vehicle):
        """Test adding a successful decode attempt."""
        # Arrange
        attempt = DecodeAttempt(
            timestamp=datetime.utcnow(),
            service_used="autodev",
            success=True,
            error_message=None
        )
        initial_count = len(sample_vehicle.decode_history)
        
        # Act
        sample_vehicle.add_decode_attempt(attempt)
        
        # Assert
        assert len(sample_vehicle.decode_history) == initial_count + 1
        assert sample_vehicle.decode_history[-1] == attempt
    
    def test_add_decode_attempt_failure(self, sample_vehicle):
        """Test adding a failed decode attempt."""
        # Arrange
        attempt = DecodeAttempt(
            timestamp=datetime.utcnow(),
            service_used="autodev",
            success=False,
            error_message="API rate limit exceeded"
        )
        
        # Act
        sample_vehicle.add_decode_attempt(attempt)
        
        # Assert
        latest_attempt = sample_vehicle.decode_history[-1]
        assert latest_attempt.success is False
        assert latest_attempt.error_message == "API rate limit exceeded"
        assert latest_attempt.service_used == "autodev"
    
    def test_decode_attempt_default_values(self):
        """Test DecodeAttempt default values."""
        # Act
        attempt = DecodeAttempt()
        
        # Assert
        assert isinstance(attempt.timestamp, datetime)
        assert attempt.service_used == ""
        assert attempt.success is True
        assert attempt.error_message is None
    
    def test_decode_attempt_custom_values(self):
        """Test DecodeAttempt with custom values."""
        # Arrange
        timestamp = datetime(2024, 1, 15, 12, 0, 0)
        service_used = "custom_service"
        success = False
        error_message = "Custom error"
        
        # Act
        attempt = DecodeAttempt(
            timestamp=timestamp,
            service_used=service_used,
            success=success,
            error_message=error_message
        )
        
        # Assert
        assert attempt.timestamp == timestamp
        assert attempt.service_used == service_used
        assert attempt.success == success
        assert attempt.error_message == error_message
    
    def test_vehicle_inherits_from_aggregate_root(self, sample_vehicle):
        """Test that Vehicle inherits from AggregateRoot."""
        # Assert
        assert hasattr(sample_vehicle, 'id')
        assert hasattr(sample_vehicle, 'created_at')
        assert hasattr(sample_vehicle, 'updated_at')
        assert hasattr(sample_vehicle, 'add_domain_event')
        assert hasattr(sample_vehicle, 'collect_events')
        assert hasattr(sample_vehicle, 'clear_events')
    
    def test_vehicle_domain_event_emission(self, sample_vin):
        """Test that vehicle emits domain events correctly."""
        # Act
        vehicle = Vehicle.create_from_decode_result(
            vin=sample_vin,
            manufacturer="Honda",
            model="Civic",
            model_year=ModelYear(2021),
            attributes={"make": "Honda"},
            service_used="nhtsa"
        )
        
        # Assert
        events = vehicle.collect_events()
        assert len(events) == 1
        
        event = events[0]
        assert isinstance(event, VehicleDecodedEvent)
        assert event.aggregate_id == vehicle.id
        assert event.vin == sample_vin.value
        assert isinstance(event.decoded_at, datetime)
    
    def test_vehicle_clear_events(self, sample_vehicle):
        """Test clearing vehicle domain events."""
        # Arrange - Ensure there are events
        sample_vehicle.add_domain_event(VehicleDecodedEvent(
            aggregate_id=sample_vehicle.id,
            vin=sample_vehicle.vin.value,
            decoded_at=datetime.utcnow()
        ))
        
        # Act
        events_before = sample_vehicle.collect_events()
        sample_vehicle.clear_events()
        events_after = sample_vehicle.collect_events()
        
        # Assert
        assert len(events_before) > 0
        assert len(events_after) == 0
    
    def test_multiple_decode_attempts_tracking(self, sample_vehicle):
        """Test tracking multiple decode attempts."""
        # Arrange
        attempts = [
            DecodeAttempt(service_used="nhtsa", success=True),
            DecodeAttempt(service_used="autodev", success=False, error_message="Rate limit"),
            DecodeAttempt(service_used="autodev", success=True)
        ]
        
        # Act
        for attempt in attempts:
            sample_vehicle.add_decode_attempt(attempt)
        
        # Assert
        # Should have original attempt + 3 new ones
        assert len(sample_vehicle.decode_history) == 4
        
        # Check services used
        services_used = [attempt.service_used for attempt in sample_vehicle.decode_history]
        assert "nhtsa" in services_used
        assert "autodev" in services_used
        
        # Check success/failure tracking
        successful_attempts = [attempt for attempt in sample_vehicle.decode_history if attempt.success]
        failed_attempts = [attempt for attempt in sample_vehicle.decode_history if not attempt.success]
        
        assert len(successful_attempts) == 3  # original + 2 new successful
        assert len(failed_attempts) == 1
    
    @pytest.mark.parametrize("manufacturer,model,expected_display", [
        ("Honda", "Civic", "Honda Civic"),
        ("Toyota", "Camry", "Toyota Camry"),
        ("", "Model", " Model"),
        ("Make", "", "Make "),
        ("", "", " "),
    ])
    def test_vehicle_display_representation(self, sample_vin, manufacturer, model, expected_display):
        """Test vehicle display representation with various make/model combinations."""
        # Arrange
        vehicle = Vehicle(
            vin=sample_vin,
            manufacturer=manufacturer,
            model=model,
            model_year=ModelYear(2021)
        )
        
        # Act
        display_name = f"{vehicle.manufacturer} {vehicle.model}"
        
        # Assert
        assert display_name == expected_display
    
    def test_vehicle_with_empty_attributes(self, sample_vin):
        """Test vehicle creation with empty attributes."""
        # Act
        vehicle = Vehicle(
            vin=sample_vin,
            manufacturer="Honda",
            model="Civic",
            model_year=ModelYear(2021),
            attributes={}
        )
        
        # Assert
        assert vehicle.attributes == {}
        assert isinstance(vehicle.attributes, dict)
    
    def test_vehicle_attributes_update_preserves_existing(self, sample_vehicle):
        """Test that attribute updates preserve existing values."""
        # Arrange
        original_attributes = sample_vehicle.attributes.copy()
        updates = {"new_field": "new_value"}
        
        # Act
        sample_vehicle.update_attributes(updates)
        
        # Assert
        # Original attributes should still be present
        for key, value in original_attributes.items():
            assert sample_vehicle.attributes[key] == value
        
        # New attribute should be added
        assert sample_vehicle.attributes["new_field"] == "new_value"

