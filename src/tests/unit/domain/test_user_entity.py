"""Unit tests for User domain entity."""

import pytest
from datetime import datetime, timedelta
from src.domain.user.entities.user import User, UserHistory
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.domain.user.events.user_events import UserCreatedEvent, UserPreferencesUpdatedEvent


@pytest.mark.unit
@pytest.mark.domain
class TestUserEntity:
    """Test cases for User domain entity."""
    
    def test_user_creation_factory_method(self, sample_telegram_id, sample_user_preferences):
        """Test user creation using factory method."""
        # Act
        user = User.create(
            telegram_id=sample_telegram_id,
            username="testuser",
            first_name="Test",
            last_name="User",
            preferences=sample_user_preferences
        )
        
        # Assert
        assert user.telegram_id == sample_telegram_id
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.preferences == sample_user_preferences
        assert user.is_active is True
        assert user.last_activity is not None
        assert len(user.history) == 0
        assert len(user.saved_vehicles) == 0
        
        # Check domain events
        events = user.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], UserCreatedEvent)
        assert events[0].telegram_id == sample_telegram_id.value
    
    def test_user_creation_with_defaults(self, sample_telegram_id):
        """Test user creation with default preferences."""
        # Act
        user = User.create(telegram_id=sample_telegram_id)
        
        # Assert
        assert user.telegram_id == sample_telegram_id
        assert user.username is None
        assert user.first_name is None
        assert user.last_name is None
        assert isinstance(user.preferences, UserPreferences)
        assert user.is_active is True
    
    def test_update_preferences(self, sample_user):
        """Test updating user preferences."""
        # Arrange
        new_preferences = UserPreferences(
            preferred_decoder="autodev",
            include_market_value=False,
            include_history=True,
            include_recalls=False,
            include_specs=False,
            format_preference="detailed"
        )
        old_preferences = sample_user.preferences
        
        # Act
        sample_user.update_preferences(new_preferences)
        
        # Assert
        assert sample_user.preferences == new_preferences
        assert sample_user.updated_at is not None
        
        # Check domain events
        events = sample_user.collect_events()
        preference_events = [e for e in events if isinstance(e, UserPreferencesUpdatedEvent)]
        assert len(preference_events) == 1
        
        event = preference_events[0]
        assert event.user_id == sample_user.id
        assert event.old_preferences == old_preferences.to_dict()
        assert event.new_preferences == new_preferences.to_dict()
    
    def test_add_to_history(self, sample_user):
        """Test adding VIN decode to user history."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        service_used = "nhtsa"
        vehicle_info = {
            "make": "Honda",
            "model": "Civic",
            "year": 2021
        }
        initial_count = len(sample_user.history)
        
        # Act
        sample_user.add_to_history(vin, service_used, vehicle_info)
        
        # Assert
        assert len(sample_user.history) == initial_count + 1
        
        latest_entry = sample_user.history[-1]
        assert isinstance(latest_entry, UserHistory)
        assert latest_entry.vin == vin
        assert latest_entry.service_used == service_used
        assert latest_entry.vehicle_info == vehicle_info
        assert latest_entry.decoded_at is not None
        assert sample_user.last_activity is not None
        assert sample_user.updated_at is not None
    
    def test_add_to_history_limits_entries(self, sample_user):
        """Test that history is limited to 100 entries."""
        # Arrange - Add 101 entries
        for i in range(101):
            sample_user.add_to_history(
                f"VIN{i:017d}",
                "nhtsa",
                {"make": "Test", "model": f"Model{i}"}
            )
        
        # Assert
        assert len(sample_user.history) == 100
        # Check that the oldest entry was removed
        assert sample_user.history[0].vehicle_info["model"] == "Model1"
        assert sample_user.history[-1].vehicle_info["model"] == "Model100"
    
    def test_save_vehicle(self, sample_user):
        """Test saving a vehicle to user's saved list."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        
        # Act
        sample_user.save_vehicle(vin)
        
        # Assert
        assert vin in sample_user.saved_vehicles
        assert sample_user.updated_at is not None
    
    def test_save_vehicle_prevents_duplicates(self, sample_user):
        """Test that saving the same vehicle twice doesn't create duplicates."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        
        # Act
        sample_user.save_vehicle(vin)
        sample_user.save_vehicle(vin)  # Save again
        
        # Assert
        assert sample_user.saved_vehicles.count(vin) == 1
    
    def test_remove_saved_vehicle_success(self, sample_user):
        """Test successfully removing a saved vehicle."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        sample_user.save_vehicle(vin)
        
        # Act
        result = sample_user.remove_saved_vehicle(vin)
        
        # Assert
        assert result is True
        assert vin not in sample_user.saved_vehicles
        assert sample_user.updated_at is not None
    
    def test_remove_saved_vehicle_not_found(self, sample_user):
        """Test removing a vehicle that wasn't saved."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        
        # Act
        result = sample_user.remove_saved_vehicle(vin)
        
        # Assert
        assert result is False
        assert vin not in sample_user.saved_vehicles
    
    def test_get_recent_history(self, sample_user):
        """Test getting recent history entries."""
        # Arrange - Add 15 history entries
        for i in range(15):
            sample_user.add_to_history(
                f"VIN{i:017d}",
                "nhtsa",
                {"make": "Test", "model": f"Model{i}"}
            )
        
        # Act
        recent_history = sample_user.get_recent_history(limit=5)
        
        # Assert
        assert len(recent_history) == 5
        # Should return the last 5 entries
        assert recent_history[0].vehicle_info["model"] == "Model10"
        assert recent_history[-1].vehicle_info["model"] == "Model14"
    
    def test_get_recent_history_empty(self, sample_user):
        """Test getting recent history when history is empty."""
        # Act
        recent_history = sample_user.get_recent_history()
        
        # Assert
        assert len(recent_history) == 0
    
    def test_deactivate_user(self, sample_user):
        """Test deactivating a user."""
        # Act
        sample_user.deactivate()
        
        # Assert
        assert sample_user.is_active is False
        assert sample_user.updated_at is not None
    
    def test_reactivate_user(self, sample_user):
        """Test reactivating a user."""
        # Arrange
        sample_user.deactivate()
        
        # Act
        sample_user.reactivate()
        
        # Assert
        assert sample_user.is_active is True
        assert sample_user.last_activity is not None
        assert sample_user.updated_at is not None
    
    def test_display_name_with_first_name(self, sample_telegram_id):
        """Test display name when first name is available."""
        # Arrange
        user = User.create(
            telegram_id=sample_telegram_id,
            first_name="John",
            username="johndoe"
        )
        
        # Act & Assert
        assert user.display_name == "John"
    
    def test_display_name_with_username_only(self, sample_telegram_id):
        """Test display name when only username is available."""
        # Arrange
        user = User.create(
            telegram_id=sample_telegram_id,
            username="johndoe"
        )
        
        # Act & Assert
        assert user.display_name == "@johndoe"
    
    def test_display_name_fallback_to_telegram_id(self, sample_telegram_id):
        """Test display name fallback to Telegram ID."""
        # Arrange
        user = User.create(telegram_id=sample_telegram_id)
        
        # Act & Assert
        assert user.display_name == f"User {sample_telegram_id.value}"
    
    def test_user_history_dataclass(self):
        """Test UserHistory dataclass."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        service_used = "nhtsa"
        vehicle_info = {"make": "Honda", "model": "Civic"}
        
        # Act
        history = UserHistory(
            vin=vin,
            service_used=service_used,
            vehicle_info=vehicle_info
        )
        
        # Assert
        assert history.vin == vin
        assert history.service_used == service_used
        assert history.vehicle_info == vehicle_info
        assert isinstance(history.decoded_at, datetime)
    
    def test_user_inherits_from_aggregate_root(self, sample_user):
        """Test that User inherits from AggregateRoot."""
        # Assert
        assert hasattr(sample_user, 'id')
        assert hasattr(sample_user, 'created_at')
        assert hasattr(sample_user, 'updated_at')
        assert hasattr(sample_user, 'add_domain_event')
        assert hasattr(sample_user, 'collect_events')
        assert hasattr(sample_user, 'clear_events')
    
    @pytest.mark.parametrize("activity_days_ago,expected_active", [
        (0, True),   # Today
        (1, True),   # Yesterday
        (7, True),   # A week ago
        (30, False), # A month ago
        (90, False), # Three months ago
    ])
    def test_user_activity_tracking(self, sample_user, activity_days_ago, expected_active, frozen_time):
        """Test user activity tracking logic."""
        # Arrange
        if activity_days_ago > 0:
            past_time = frozen_time - timedelta(days=activity_days_ago)
            sample_user.last_activity = past_time
        
        # Act - This would typically be part of a domain service
        # For now, we just check the last_activity value
        days_since_activity = (frozen_time - sample_user.last_activity).days
        is_recently_active = days_since_activity < 30
        
        # Assert
        assert is_recently_active == expected_active
