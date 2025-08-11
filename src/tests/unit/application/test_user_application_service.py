"""Unit tests for UserApplicationService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.application.user.services.user_application_service import UserApplicationService
from src.domain.user.entities.user import User
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.domain.user.events.user_events import UserCreatedEvent


@pytest.mark.unit
@pytest.mark.application
class TestUserApplicationService:
    """Test cases for UserApplicationService."""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_logger(self):
        """Mock logger."""
        return MagicMock()
    
    @pytest.fixture
    def user_service(self, mock_user_repository, mock_event_bus, mock_logger):
        """Create UserApplicationService instance with mocked dependencies."""
        return UserApplicationService(
            user_repository=mock_user_repository,
            event_bus=mock_event_bus,
            logger=mock_logger
        )
    
    async def test_get_or_create_user_existing_user(
        self,
        user_service,
        sample_user,
        mock_user_repository,
        mock_event_bus
    ):
        """Test getting an existing user."""
        # Arrange
        telegram_id = sample_user.telegram_id
        mock_user_repository.find_by_telegram_id.return_value = sample_user
        
        # Act
        result = await user_service.get_or_create_user(
            telegram_id=telegram_id.value,
            username=sample_user.username,
            first_name=sample_user.first_name,
            last_name=sample_user.last_name
        )
        
        # Assert
        assert result == sample_user
        mock_user_repository.find_by_telegram_id.assert_called_once_with(telegram_id)
        mock_user_repository.save.assert_not_called()
        mock_event_bus.publish.assert_not_called()
    
    async def test_get_or_create_user_new_user(
        self,
        user_service,
        sample_telegram_id,
        mock_user_repository,
        mock_event_bus
    ):
        """Test creating a new user."""
        # Arrange
        mock_user_repository.find_by_telegram_id.return_value = None
        username = "newuser"
        first_name = "New"
        last_name = "User"
        
        # Act
        result = await user_service.get_or_create_user(
            telegram_id=sample_telegram_id.value,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        # Assert
        assert isinstance(result, User)
        assert result.telegram_id == sample_telegram_id
        assert result.username == username
        assert result.first_name == first_name
        assert result.last_name == last_name
        
        # Verify user was saved
        mock_user_repository.save.assert_called_once()
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user == result
        
        # Verify events were published
        mock_event_bus.publish.assert_called()
        published_event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(published_event, UserCreatedEvent)
    
    async def test_get_or_create_user_minimal_data(
        self,
        user_service,
        sample_telegram_id,
        mock_user_repository,
        mock_event_bus
    ):
        """Test creating a user with minimal data."""
        # Arrange
        mock_user_repository.find_by_telegram_id.return_value = None
        
        # Act
        result = await user_service.get_or_create_user(
            telegram_id=sample_telegram_id.value
        )
        
        # Assert
        assert isinstance(result, User)
        assert result.telegram_id == sample_telegram_id
        assert result.username is None
        assert result.first_name is None
        assert result.last_name is None
        
        # Verify user was saved and events published
        mock_user_repository.save.assert_called_once()
        mock_event_bus.publish.assert_called()
    
    async def test_update_user_preferences(
        self,
        user_service,
        sample_user,
        mock_user_repository,
        mock_event_bus
    ):
        """Test updating user preferences."""
        # Arrange
        new_preferences = UserPreferences(
            preferred_decoder="autodev",
            include_market_value=False,
            include_history=True
        )
        
        # Act
        result = await user_service.update_user_preferences(
            user_id=sample_user.id,
            preferences=new_preferences
        )
        
        # Assert
        assert result == sample_user
        assert sample_user.preferences == new_preferences
        
        # Verify user was saved
        mock_user_repository.save.assert_called_once_with(sample_user)
        
        # Verify events were published
        mock_event_bus.publish.assert_called()
    
    async def test_update_user_preferences_user_not_found(
        self,
        user_service,
        mock_user_repository
    ):
        """Test updating preferences for non-existent user."""
        # Arrange
        user_id = "non-existent-id"
        new_preferences = UserPreferences()
        mock_user_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await user_service.update_user_preferences(
                user_id=user_id,
                preferences=new_preferences
            )
        
        assert "User not found" in str(exc_info.value)
        mock_user_repository.save.assert_not_called()
    
    async def test_add_user_decode_history(
        self,
        user_service,
        sample_user,
        mock_user_repository,
        mock_event_bus
    ):
        """Test adding decode history to user."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        service_used = "nhtsa"
        vehicle_info = {
            "make": "Honda",
            "model": "Civic",
            "year": 2021
        }
        initial_history_count = len(sample_user.history)
        
        # Act
        await user_service.add_user_decode_history(
            user_id=sample_user.id,
            vin=vin,
            service_used=service_used,
            vehicle_info=vehicle_info
        )
        
        # Assert
        assert len(sample_user.history) == initial_history_count + 1
        latest_entry = sample_user.history[-1]
        assert latest_entry.vin == vin
        assert latest_entry.service_used == service_used
        assert latest_entry.vehicle_info == vehicle_info
        
        # Verify user was saved
        mock_user_repository.save.assert_called_once_with(sample_user)
    
    async def test_add_user_decode_history_user_not_found(
        self,
        user_service,
        mock_user_repository
    ):
        """Test adding decode history for non-existent user."""
        # Arrange
        user_id = "non-existent-id"
        mock_user_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await user_service.add_user_decode_history(
                user_id=user_id,
                vin="1HGBH41JXMN109186",
                service_used="nhtsa",
                vehicle_info={}
            )
        
        assert "User not found" in str(exc_info.value)
    
    async def test_save_user_vehicle(
        self,
        user_service,
        sample_user,
        mock_user_repository
    ):
        """Test saving a vehicle for a user."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        initial_saved_count = len(sample_user.saved_vehicles)
        
        # Act
        await user_service.save_user_vehicle(
            user_id=sample_user.id,
            vin=vin
        )
        
        # Assert
        assert len(sample_user.saved_vehicles) == initial_saved_count + 1
        assert vin in sample_user.saved_vehicles
        
        # Verify user was saved
        mock_user_repository.save.assert_called_once_with(sample_user)
    
    async def test_save_user_vehicle_user_not_found(
        self,
        user_service,
        mock_user_repository
    ):
        """Test saving vehicle for non-existent user."""
        # Arrange
        user_id = "non-existent-id"
        mock_user_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await user_service.save_user_vehicle(
                user_id=user_id,
                vin="1HGBH41JXMN109186"
            )
        
        assert "User not found" in str(exc_info.value)
    
    async def test_remove_user_vehicle(
        self,
        user_service,
        sample_user,
        mock_user_repository
    ):
        """Test removing a saved vehicle from user."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        sample_user.save_vehicle(vin)  # Add vehicle first
        
        # Act
        result = await user_service.remove_user_vehicle(
            user_id=sample_user.id,
            vin=vin
        )
        
        # Assert
        assert result is True
        assert vin not in sample_user.saved_vehicles
        
        # Verify user was saved
        mock_user_repository.save.assert_called_once_with(sample_user)
    
    async def test_remove_user_vehicle_not_saved(
        self,
        user_service,
        sample_user,
        mock_user_repository
    ):
        """Test removing a vehicle that wasn't saved."""
        # Arrange
        vin = "1HGBH41JXMN109186"
        # Don't add vehicle to saved list
        
        # Act
        result = await user_service.remove_user_vehicle(
            user_id=sample_user.id,
            vin=vin
        )
        
        # Assert
        assert result is False
        
        # User should still be saved (updated_at changes)
        mock_user_repository.save.assert_called_once_with(sample_user)
    
    async def test_remove_user_vehicle_user_not_found(
        self,
        user_service,
        mock_user_repository
    ):
        """Test removing vehicle for non-existent user."""
        # Arrange
        user_id = "non-existent-id"
        mock_user_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await user_service.remove_user_vehicle(
                user_id=user_id,
                vin="1HGBH41JXMN109186"
            )
        
        assert "User not found" in str(exc_info.value)
    
    async def test_get_user_recent_history(
        self,
        user_service,
        sample_user,
        mock_user_repository
    ):
        """Test getting user's recent decode history."""
        # Arrange
        # Add some history entries
        for i in range(5):
            sample_user.add_to_history(
                vin=f"VIN{i:017d}",
                service_used="nhtsa",
                vehicle_info={"make": "Test", "model": f"Model{i}"}
            )
        
        # Act
        result = await user_service.get_user_recent_history(
            user_id=sample_user.id,
            limit=3
        )
        
        # Assert
        assert len(result) == 3
        # Should return the most recent entries
        assert result[0].vehicle_info["model"] == "Model2"
        assert result[-1].vehicle_info["model"] == "Model4"
    
    async def test_get_user_recent_history_user_not_found(
        self,
        user_service,
        mock_user_repository
    ):
        """Test getting history for non-existent user."""
        # Arrange
        user_id = "non-existent-id"
        mock_user_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await user_service.get_user_recent_history(
                user_id=user_id,
                limit=10
            )
        
        assert "User not found" in str(exc_info.value)
    
    async def test_deactivate_user(
        self,
        user_service,
        sample_user,
        mock_user_repository
    ):
        """Test deactivating a user."""
        # Arrange
        assert sample_user.is_active is True
        
        # Act
        await user_service.deactivate_user(user_id=sample_user.id)
        
        # Assert
        assert sample_user.is_active is False
        mock_user_repository.save.assert_called_once_with(sample_user)
    
    async def test_reactivate_user(
        self,
        user_service,
        sample_user,
        mock_user_repository
    ):
        """Test reactivating a user."""
        # Arrange
        sample_user.deactivate()
        assert sample_user.is_active is False
        
        # Act
        await user_service.reactivate_user(user_id=sample_user.id)
        
        # Assert
        assert sample_user.is_active is True
        mock_user_repository.save.assert_called_once_with(sample_user)
    
    async def test_user_service_handles_repository_errors(
        self,
        user_service,
        sample_telegram_id,
        mock_user_repository,
        mock_logger
    ):
        """Test that service handles repository errors gracefully."""
        # Arrange
        mock_user_repository.find_by_telegram_id.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await user_service.get_or_create_user(
                telegram_id=sample_telegram_id.value
            )
        
        assert "Database error" in str(exc_info.value)
        mock_logger.error.assert_called()
    
    async def test_user_service_publishes_domain_events(
        self,
        user_service,
        sample_user,
        mock_user_repository,
        mock_event_bus
    ):
        """Test that service publishes domain events from aggregates."""
        # Arrange
        new_preferences = UserPreferences(preferred_decoder="autodev")
        
        # Act
        await user_service.update_user_preferences(
            user_id=sample_user.id,
            preferences=new_preferences
        )
        
        # Assert
        # Should publish events that were generated by the user aggregate
        mock_event_bus.publish.assert_called()
        
        # Verify the published event is from user's domain events
        published_events = [call[0][0] for call in mock_event_bus.publish.call_args_list]
        assert len(published_events) > 0
        
        # Should have UserPreferencesUpdatedEvent
        from src.domain.user.events.user_events import UserPreferencesUpdatedEvent
        preference_events = [e for e in published_events if isinstance(e, UserPreferencesUpdatedEvent)]
        assert len(preference_events) == 1

