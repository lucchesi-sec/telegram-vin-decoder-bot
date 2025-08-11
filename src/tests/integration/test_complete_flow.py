"""Integration tests for complete application flow."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime

from src.config.dependencies import Container
from src.config.settings import Settings
from src.domain.user.entities.user import User
from src.domain.vehicle.entities.vehicle import Vehicle
from src.domain.vehicle.value_objects.vin_number import VINNumber
from src.application.vehicle.services.vehicle_application_service import VehicleApplicationService
from src.application.user.services.user_application_service import UserApplicationService
from src.infrastructure.persistence.repositories.in_memory_user_repository import InMemoryUserRepository
from src.infrastructure.persistence.repositories.in_memory_vehicle_repository import InMemoryVehicleRepository
from src.tests.utils.factories import VINFactory, UserFactory, VehicleFactory, APIResponseFactory
from src.tests.utils.helpers import MockResponse


class TestCompleteVINDecodeFlow:
    """Test complete VIN decode flow from request to response."""
    
    @pytest_asyncio.fixture
    async def container(self, mock_settings):
        """Create a fully configured DI container."""
        container = Container()
        container.config.from_dict(mock_settings)
        
        # Override with in-memory repositories for testing
        container.user_repository.override(InMemoryUserRepository())
        container.vehicle_repository.override(InMemoryVehicleRepository())
        
        return container
    
    @pytest_asyncio.fixture
    async def vehicle_service(self, container):
        """Get vehicle application service from container."""
        return container.vehicle_application_service()
    
    @pytest_asyncio.fixture
    async def user_service(self, container):
        """Get user application service from container."""
        return container.user_application_service()
    
    @pytest.mark.asyncio
    async def test_complete_vin_decode_flow(self, vehicle_service, user_service):
        """Test complete flow from user request to VIN decode result."""
        # Step 1: Create or get user
        telegram_id = 123456789
        user = await user_service.get_or_create_user(
            telegram_id=telegram_id,
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        assert user is not None
        assert user.telegram_id.value == telegram_id
        
        # Step 2: Mock external API response
        vin = "1HGBH41JXMN109186"
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = MockResponse(
                status_code=200,
                json_data=APIResponseFactory.create_nhtsa_response(vin)
            )
            
            # Step 3: Decode VIN
            result = await vehicle_service.decode_vin(
                vin=vin,
                user_id=telegram_id,
                decoder_service="nhtsa",
                save_to_history=True
            )
            
            # Step 4: Verify result
            assert result.success is True
            assert result.vin == vin
            assert result.manufacturer == "Honda"
            assert result.model == "Civic"
            
            # Step 5: Check that vehicle was saved to history
            recent_vehicles = await vehicle_service.get_recent_vehicles(
                user_id=telegram_id,
                limit=5
            )
            assert len(recent_vehicles) == 1
            assert recent_vehicles[0].vin.value == vin
            
            # Step 6: Update user preferences
            await user_service.update_user_preferences(
                telegram_id=telegram_id,
                preferences={
                    "preferred_decoder": "autodev",
                    "include_market_value": True
                }
            )
            
            # Step 7: Get updated user and verify preferences
            updated_user = await user_service.get_user(telegram_id)
            assert updated_user.preferences.preferred_decoder == "autodev"
            assert updated_user.preferences.include_market_value is True
    
    @pytest.mark.asyncio
    async def test_concurrent_vin_decoding(self, vehicle_service):
        """Test concurrent VIN decoding for multiple users."""
        vins = [VINFactory.create_valid_vin(i) for i in range(5)]
        user_ids = [100000 + i for i in range(5)]
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock responses for all VINs
            responses = []
            for vin in vins:
                responses.append(MockResponse(
                    status_code=200,
                    json_data=APIResponseFactory.create_nhtsa_response(vin)
                ))
            mock_client.get.side_effect = responses
            
            # Decode VINs concurrently
            tasks = []
            for vin, user_id in zip(vins, user_ids):
                task = vehicle_service.decode_vin(
                    vin=vin,
                    user_id=user_id,
                    decoder_service="nhtsa"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # Verify all succeeded
            assert len(results) == 5
            for result, vin in zip(results, vins):
                assert result.success is True
                assert result.vin == vin
    
    @pytest.mark.asyncio
    async def test_fallback_decoder_flow(self, vehicle_service):
        """Test fallback to alternative decoder when primary fails."""
        vin = "1HGBH41JXMN109186"
        user_id = 123456789
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # First call to NHTSA fails
            # Second call to AutoDev succeeds
            mock_client.get.side_effect = [
                MockResponse(status_code=500, raise_on_status=True),
                MockResponse(
                    status_code=200,
                    json_data=APIResponseFactory.create_autodev_response(vin)
                )
            ]
            
            result = await vehicle_service.decode_vin(
                vin=vin,
                user_id=user_id,
                decoder_service="nhtsa",
                fallback_service="autodev"
            )
            
            assert result.success is True
            assert result.service_used == "autodev"
            assert mock_client.get.call_count == 2
    
    @pytest.mark.asyncio
    async def test_cache_hit_flow(self, vehicle_service):
        """Test that cached results are returned without API call."""
        vin = "1HGBH41JXMN109186"
        user_id = 123456789
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = MockResponse(
                status_code=200,
                json_data=APIResponseFactory.create_nhtsa_response(vin)
            )
            
            # First decode - should hit API
            result1 = await vehicle_service.decode_vin(
                vin=vin,
                user_id=user_id,
                decoder_service="nhtsa"
            )
            assert result1.success is True
            assert mock_client.get.call_count == 1
            
            # Second decode - should hit cache
            result2 = await vehicle_service.decode_vin(
                vin=vin,
                user_id=user_id,
                decoder_service="nhtsa"
            )
            assert result2.success is True
            assert result2.vin == result1.vin
            # API should not be called again
            assert mock_client.get.call_count == 1
    
    @pytest.mark.asyncio
    async def test_error_recovery_flow(self, vehicle_service):
        """Test error recovery and retry mechanisms."""
        vin = "1HGBH41JXMN109186"
        user_id = 123456789
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Simulate temporary failures then success
            mock_client.get.side_effect = [
                MockResponse(status_code=503, raise_on_status=True),  # Service unavailable
                MockResponse(status_code=503, raise_on_status=True),  # Service unavailable
                MockResponse(
                    status_code=200,
                    json_data=APIResponseFactory.create_nhtsa_response(vin)
                )
            ]
            
            result = await vehicle_service.decode_vin(
                vin=vin,
                user_id=user_id,
                decoder_service="nhtsa",
                retry_count=2
            )
            
            assert result.success is True
            assert mock_client.get.call_count == 3


class TestUserManagementFlow:
    """Test user management and preferences flow."""
    
    @pytest_asyncio.fixture
    async def user_repository(self):
        """Create in-memory user repository."""
        return InMemoryUserRepository()
    
    @pytest_asyncio.fixture
    async def user_service(self, user_repository):
        """Create user application service."""
        return UserApplicationService(
            user_repository=user_repository,
            event_bus=AsyncMock()
        )
    
    @pytest.mark.asyncio
    async def test_user_lifecycle(self, user_service):
        """Test complete user lifecycle from creation to deletion."""
        telegram_id = 123456789
        
        # Step 1: Create new user
        user = await user_service.get_or_create_user(
            telegram_id=telegram_id,
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        assert user is not None
        assert user.telegram_id.value == telegram_id
        
        # Step 2: Update preferences
        await user_service.update_user_preferences(
            telegram_id=telegram_id,
            preferences={
                "preferred_decoder": "autodev",
                "include_market_value": True,
                "include_history": True,
                "format_preference": "detailed"
            }
        )
        
        # Step 3: Get user statistics
        stats = await user_service.get_user_statistics(telegram_id)
        assert stats is not None
        
        # Step 4: Get user again (should return existing)
        existing_user = await user_service.get_or_create_user(
            telegram_id=telegram_id,
            username="testuser"
        )
        assert existing_user.id == user.id
        assert existing_user.preferences.preferred_decoder == "autodev"
        
        # Step 5: Delete user
        await user_service.delete_user(telegram_id)
        
        # Step 6: Verify user is deleted
        deleted_user = await user_service.get_user(telegram_id)
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_concurrent_user_operations(self, user_service):
        """Test concurrent operations on multiple users."""
        user_ids = [100000 + i for i in range(10)]
        
        # Create users concurrently
        create_tasks = []
        for user_id in user_ids:
            task = user_service.get_or_create_user(
                telegram_id=user_id,
                username=f"user_{user_id}"
            )
            create_tasks.append(task)
        
        users = await asyncio.gather(*create_tasks)
        assert len(users) == 10
        
        # Update preferences concurrently
        update_tasks = []
        for user_id in user_ids:
            task = user_service.update_user_preferences(
                telegram_id=user_id,
                preferences={"preferred_decoder": "nhtsa"}
            )
            update_tasks.append(task)
        
        await asyncio.gather(*update_tasks)
        
        # Verify all users have updated preferences
        for user_id in user_ids:
            user = await user_service.get_user(user_id)
            assert user.preferences.preferred_decoder == "nhtsa"


class TestEndToEndTelegramFlow:
    """Test end-to-end Telegram bot flow."""
    
    @pytest.mark.asyncio
    async def test_telegram_command_flow(self, mock_container):
        """Test complete flow from Telegram command to response."""
        from src.presentation.telegram_bot.bot_application import BotApplication
        
        with patch('telegram.ext.ApplicationBuilder') as mock_app_builder:
            mock_app = AsyncMock()
            mock_app_builder.return_value.token.return_value.build.return_value = mock_app
            
            bot = BotApplication(mock_container)
            
            # Simulate /start command
            mock_update = MagicMock()
            mock_update.effective_user.id = 123456789
            mock_update.effective_user.username = "testuser"
            mock_update.message.text = "/start"
            
            mock_context = MagicMock()
            mock_context.bot = AsyncMock()
            
            # Process command
            await bot.command_handlers.start_command(mock_update, mock_context)
            
            # Verify response was sent
            mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_callback_query_flow(self, mock_container):
        """Test callback query processing flow."""
        from src.presentation.telegram_bot.bot_application import BotApplication
        
        bot = BotApplication(mock_container)
        
        mock_update = MagicMock()
        mock_update.callback_query.data = "settings:decoder:autodev"
        mock_update.effective_user.id = 123456789
        
        mock_context = MagicMock()
        
        await bot.callback_handlers.handle_callback(mock_update, mock_context)
        
        mock_update.callback_query.answer.assert_called()
    
    @pytest.mark.asyncio
    async def test_error_handling_flow(self, mock_container):
        """Test error handling in bot flow."""
        from src.presentation.telegram_bot.bot_application import BotApplication
        
        bot = BotApplication(mock_container)
        
        mock_update = MagicMock()
        mock_update.message.text = "/vin INVALID"
        mock_update.effective_user.id = 123456789
        
        mock_context = MagicMock()
        mock_context.args = ["INVALID"]
        
        await bot.command_handlers.vin_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called()
        reply_text = mock_update.message.reply_text.call_args[0][0]
        assert "Invalid" in reply_text or "error" in reply_text.lower()