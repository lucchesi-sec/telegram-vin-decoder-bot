"""Unit tests for Telegram command handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.presentation.telegram_bot.handlers.command_handlers import CommandHandlers
from src.tests.utils.helpers import (
    create_mock_telegram_update,
    create_mock_telegram_context,
    create_mock_telegram_message,
    create_mock_telegram_user
)
from src.tests.utils.factories import UserFactory, VehicleFactory


class TestCommandHandlers:
    """Test Telegram command handlers."""
    
    @pytest.fixture
    def mock_vehicle_service(self):
        """Create mock vehicle application service."""
        service = AsyncMock()
        service.decode_vin = AsyncMock()
        service.get_recent_vehicles = AsyncMock(return_value=[])
        service.get_vehicle_by_vin = AsyncMock(return_value=None)
        return service
    
    @pytest.fixture
    def mock_user_service(self):
        """Create mock user application service."""
        service = AsyncMock()
        service.get_or_create_user = AsyncMock(return_value=UserFactory.create_user())
        service.update_user_preferences = AsyncMock()
        service.get_user_statistics = AsyncMock(return_value={
            "total_searches": 10,
            "favorite_decoder": "nhtsa"
        })
        return service
    
    @pytest.fixture
    def command_handlers(self, mock_vehicle_service, mock_user_service):
        """Create CommandHandlers instance."""
        return CommandHandlers(
            vehicle_service=mock_vehicle_service,
            user_service=mock_user_service
        )
    
    @pytest.mark.asyncio
    async def test_start_command(self, command_handlers, mock_user_service):
        """Test /start command handler."""
        user = create_mock_telegram_user(user_id=123456789, username="testuser")
        message = create_mock_telegram_message(text="/start", user=user)
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        
        await command_handlers.start_command(update, context)
        
        mock_user_service.get_or_create_user.assert_called_once()
        message.reply_text.assert_called_once()
        reply_text = message.reply_text.call_args[0][0]
        assert "Welcome" in reply_text
        assert "VIN Decoder Bot" in reply_text
    
    @pytest.mark.asyncio
    async def test_help_command(self, command_handlers):
        """Test /help command handler."""
        message = create_mock_telegram_message(text="/help")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        
        await command_handlers.help_command(update, context)
        
        message.reply_text.assert_called_once()
        reply_text = message.reply_text.call_args[0][0]
        assert "Available commands" in reply_text
        assert "/vin" in reply_text
        assert "/recent" in reply_text
        assert "/settings" in reply_text
    
    @pytest.mark.asyncio
    async def test_vin_command_valid(self, command_handlers, mock_vehicle_service):
        """Test /vin command with valid VIN."""
        valid_vin = "1HGBH41JXMN109186"
        message = create_mock_telegram_message(text=f"/vin {valid_vin}")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        context.args = [valid_vin]
        
        mock_vehicle_service.decode_vin.return_value = MagicMock(
            success=True,
            manufacturer="Honda",
            model="Civic",
            model_year=2021,
            get_display_string=lambda: "2021 Honda Civic"
        )
        
        await command_handlers.vin_command(update, context)
        
        mock_vehicle_service.decode_vin.assert_called_once_with(
            vin=valid_vin,
            user_id=123456789,
            decoder_service=None
        )
        message.reply_text.assert_called()
        reply_text = message.reply_text.call_args[0][0]
        assert "Honda" in reply_text
        assert "Civic" in reply_text
    
    @pytest.mark.asyncio
    async def test_vin_command_invalid(self, command_handlers):
        """Test /vin command with invalid VIN."""
        invalid_vin = "INVALID123"
        message = create_mock_telegram_message(text=f"/vin {invalid_vin}")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        context.args = [invalid_vin]
        
        await command_handlers.vin_command(update, context)
        
        message.reply_text.assert_called_once()
        reply_text = message.reply_text.call_args[0][0]
        assert "Invalid VIN" in reply_text or "must be 17 characters" in reply_text
    
    @pytest.mark.asyncio
    async def test_vin_command_no_args(self, command_handlers):
        """Test /vin command without arguments."""
        message = create_mock_telegram_message(text="/vin")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        context.args = []
        
        await command_handlers.vin_command(update, context)
        
        message.reply_text.assert_called_once()
        reply_text = message.reply_text.call_args[0][0]
        assert "Please provide a VIN" in reply_text
    
    @pytest.mark.asyncio
    async def test_recent_command_with_results(self, command_handlers, mock_vehicle_service):
        """Test /recent command with recent vehicles."""
        vehicles = [
            VehicleFactory.create_vehicle(manufacturer="Honda", model="Civic"),
            VehicleFactory.create_vehicle(manufacturer="Toyota", model="Camry"),
        ]
        mock_vehicle_service.get_recent_vehicles.return_value = vehicles
        
        message = create_mock_telegram_message(text="/recent")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        
        await command_handlers.recent_command(update, context)
        
        mock_vehicle_service.get_recent_vehicles.assert_called_once_with(
            user_id=123456789,
            limit=10
        )
        message.reply_text.assert_called_once()
        reply_text = message.reply_text.call_args[0][0]
        assert "Recent searches" in reply_text
        assert "Honda Civic" in reply_text
        assert "Toyota Camry" in reply_text
    
    @pytest.mark.asyncio
    async def test_recent_command_no_results(self, command_handlers, mock_vehicle_service):
        """Test /recent command with no recent vehicles."""
        mock_vehicle_service.get_recent_vehicles.return_value = []
        
        message = create_mock_telegram_message(text="/recent")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        
        await command_handlers.recent_command(update, context)
        
        message.reply_text.assert_called_once()
        reply_text = message.reply_text.call_args[0][0]
        assert "No recent searches" in reply_text
    
    @pytest.mark.asyncio
    async def test_settings_command(self, command_handlers, mock_user_service):
        """Test /settings command."""
        user = UserFactory.create_user()
        mock_user_service.get_or_create_user.return_value = user
        
        message = create_mock_telegram_message(text="/settings")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        
        await command_handlers.settings_command(update, context)
        
        message.reply_text.assert_called_once()
        call_kwargs = message.reply_text.call_args[1]
        assert 'reply_markup' in call_kwargs
        reply_text = message.reply_text.call_args[0][0]
        assert "Settings" in reply_text
    
    @pytest.mark.asyncio
    async def test_stats_command(self, command_handlers, mock_user_service):
        """Test /stats command."""
        mock_user_service.get_user_statistics.return_value = {
            "total_searches": 25,
            "favorite_decoder": "nhtsa",
            "unique_manufacturers": 5,
            "last_search_date": datetime.utcnow()
        }
        
        message = create_mock_telegram_message(text="/stats")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        
        await command_handlers.stats_command(update, context)
        
        mock_user_service.get_user_statistics.assert_called_once_with(123456789)
        message.reply_text.assert_called_once()
        reply_text = message.reply_text.call_args[0][0]
        assert "Statistics" in reply_text
        assert "25" in reply_text
        assert "nhtsa" in reply_text
    
    @pytest.mark.asyncio
    async def test_inline_vin_processing(self, command_handlers, mock_vehicle_service):
        """Test processing VIN sent as plain text."""
        valid_vin = "1HGBH41JXMN109186"
        message = create_mock_telegram_message(text=valid_vin)
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        
        mock_vehicle_service.decode_vin.return_value = MagicMock(
            success=True,
            manufacturer="Honda",
            model="Civic",
            model_year=2021
        )
        
        await command_handlers.process_message(update, context)
        
        mock_vehicle_service.decode_vin.assert_called_once()
        message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, command_handlers, mock_vehicle_service):
        """Test error handling in command handlers."""
        message = create_mock_telegram_message(text="/vin 1HGBH41JXMN109186")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        context.args = ["1HGBH41JXMN109186"]
        
        mock_vehicle_service.decode_vin.side_effect = Exception("Service error")
        
        await command_handlers.vin_command(update, context)
        
        message.reply_text.assert_called()
        reply_text = message.reply_text.call_args[0][0]
        assert "error" in reply_text.lower() or "failed" in reply_text.lower()
    
    @pytest.mark.asyncio
    async def test_command_with_rate_limiting(self, command_handlers):
        """Test rate limiting on commands."""
        message = create_mock_telegram_message(text="/vin 1HGBH41JXMN109186")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        context.args = ["1HGBH41JXMN109186"]
        
        # Simulate rate limit exceeded
        with patch.object(command_handlers, 'check_rate_limit', return_value=False):
            await command_handlers.vin_command(update, context)
            
            message.reply_text.assert_called_once()
            reply_text = message.reply_text.call_args[0][0]
            assert "rate limit" in reply_text.lower() or "too many requests" in reply_text.lower()
    
    @pytest.mark.asyncio
    async def test_command_logging(self, command_handlers, caplog):
        """Test that commands are properly logged."""
        message = create_mock_telegram_message(text="/start")
        update = create_mock_telegram_update(message=message)
        context = create_mock_telegram_context()
        
        with caplog.at_level("INFO"):
            await command_handlers.start_command(update, context)
            
            assert "start command" in caplog.text.lower()
            assert "123456789" in caplog.text  # User ID should be logged