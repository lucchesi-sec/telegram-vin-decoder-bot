"""End-to-end tests for Telegram bot flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.presentation.telegram_bot.bot_application import BotApplication
from src.presentation.telegram_bot.handlers.command_handlers import CommandHandlers
from src.presentation.telegram_bot.handlers.callback_handlers import CallbackHandlers
from src.config.dependencies import Container


@pytest.mark.e2e
@pytest.mark.telegram
class TestTelegramBotFlow:
    """End-to-end tests for Telegram bot functionality."""
    
    @pytest.fixture
    def mock_telegram_application(self):
        """Mock Telegram Application."""
        return AsyncMock()
    
    @pytest.fixture
    def bot_application(self, mock_container, mock_telegram_application):
        """Create BotApplication with mocked dependencies."""
        with patch('telegram.ext.Application.builder') as mock_builder:
            mock_builder.return_value.token.return_value.build.return_value = mock_telegram_application
            
            app = BotApplication()
            app.container = mock_container
            return app
    
    async def test_start_command_new_user(
        self,
        bot_application,
        mock_telegram_update,
        mock_telegram_context,
        mock_container
    ):
        """Test /start command for new user."""
        # Arrange
        mock_telegram_update.message.text = "/start"
        mock_user_service = AsyncMock()
        mock_container.user_application_service.return_value = mock_user_service
        
        # Mock user creation
        from src.domain.user.entities.user import User
        from src.domain.user.value_objects.telegram_id import TelegramID
        
        new_user = User.create(
            telegram_id=TelegramID(123456789),
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        mock_user_service.get_or_create_user.return_value = new_user
        
        # Create command handler
        command_handlers = CommandHandlers()
        
        # Act
        await command_handlers.start_command(mock_telegram_update, mock_telegram_context)
        
        # Assert
        mock_user_service.get_or_create_user.assert_called_once()
        mock_telegram_context.bot.send_message.assert_called()
        
        # Check welcome message was sent
        send_message_call = mock_telegram_context.bot.send_message.call_args
        assert "Welcome" in send_message_call[1]["text"]
    
    async def test_vin_decode_command_success(
        self,
        bot_application,
        mock_telegram_update,
        mock_telegram_context,
        mock_container,
        mock_nhtsa_response
    ):
        """Test VIN decode command with successful decode."""
        # Arrange
        test_vin = "1HGBH41JXMN109186"
        mock_telegram_update.message.text = f"/vin {test_vin}"
        
        # Mock user service
        mock_user_service = AsyncMock()
        mock_container.user_application_service.return_value = mock_user_service
        
        from src.domain.user.entities.user import User
        from src.domain.user.value_objects.telegram_id import TelegramID
        
        user = User.create(telegram_id=TelegramID(123456789))
        mock_user_service.get_or_create_user.return_value = user
        
        # Mock vehicle service
        mock_vehicle_service = AsyncMock()
        mock_container.vehicle_application_service.return_value = mock_vehicle_service
        
        from src.domain.vehicle.value_objects.decode_result import DecodeResult
        from src.domain.vehicle.value_objects.vin_number import VINNumber
        
        mock_decode_result = DecodeResult(
            vin=VINNumber(test_vin),
            success=True,
            data={
                "make": "Honda",
                "model": "Civic",
                "year": 2021,
                "body_type": "Sedan"
            },
            service_used="nhtsa"
        )
        mock_vehicle_service.decode_vin.return_value = mock_decode_result
        
        # Mock external API
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_nhtsa_response
            mock_response.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Create command handler
            command_handlers = CommandHandlers()
            
            # Act
            await command_handlers.vin_command(mock_telegram_update, mock_telegram_context)
            
            # Assert
            mock_vehicle_service.decode_vin.assert_called_once()
            mock_telegram_context.bot.send_message.assert_called()
            
            # Check that vehicle information was sent
            send_message_call = mock_telegram_context.bot.send_message.call_args
            message_text = send_message_call[1]["text"]
            assert "Honda" in message_text
            assert "Civic" in message_text
            assert "2021" in message_text
    
    async def test_vin_decode_command_invalid_vin(
        self,
        bot_application,
        mock_telegram_update,
        mock_telegram_context,
        mock_container
    ):
        """Test VIN decode command with invalid VIN."""
        # Arrange
        invalid_vin = "INVALID_VIN"
        mock_telegram_update.message.text = f"/vin {invalid_vin}"
        
        # Mock user service
        mock_user_service = AsyncMock()
        mock_container.user_application_service.return_value = mock_user_service
        
        from src.domain.user.entities.user import User
        from src.domain.user.value_objects.telegram_id import TelegramID
        
        user = User.create(telegram_id=TelegramID(123456789))
        mock_user_service.get_or_create_user.return_value = user
        
        # Create command handler
        command_handlers = CommandHandlers()
        
        # Act
        await command_handlers.vin_command(mock_telegram_update, mock_telegram_context)
        
        # Assert
        mock_telegram_context.bot.send_message.assert_called()
        
        # Check that error message was sent
        send_message_call = mock_telegram_context.bot.send_message.call_args
        message_text = send_message_call[1]["text"]
        assert "invalid" in message_text.lower() or "error" in message_text.lower()
    
    async def test_settings_command_and_callback(
        self,
        bot_application,
        mock_telegram_update,
        mock_telegram_context,
        mock_container
    ):
        """Test settings command and callback handling."""
        # Arrange
        mock_telegram_update.message.text = "/settings"
        
        # Mock user service
        mock_user_service = AsyncMock()
        mock_container.user_application_service.return_value = mock_user_service
        
        from src.domain.user.entities.user import User
        from src.domain.user.value_objects.telegram_id import TelegramID
        
        user = User.create(telegram_id=TelegramID(123456789))
        mock_user_service.get_or_create_user.return_value = user
        
        # Create command handler
        command_handlers = CommandHandlers()
        
        # Act
        await command_handlers.settings_command(mock_telegram_update, mock_telegram_context)
        
        # Assert
        mock_telegram_context.bot.send_message.assert_called()
        
        # Check that settings keyboard was sent
        send_message_call = mock_telegram_context.bot.send_message.call_args
        assert "reply_markup" in send_message_call[1]
    
    async def test_callback_query_handling(
        self,
        bot_application,
        mock_container
    ):
        """Test callback query handling."""
        # Arrange
        mock_update = MagicMock()
        mock_context = MagicMock()
        
        # Mock callback query
        mock_update.callback_query.data = "settings_decoder_nhtsa"
        mock_update.callback_query.from_user.id = 123456789
        mock_update.callback_query.message.chat.id = 123456789
        
        # Mock user service
        mock_user_service = AsyncMock()
        mock_container.user_application_service.return_value = mock_user_service
        
        from src.domain.user.entities.user import User
        from src.domain.user.value_objects.telegram_id import TelegramID
        
        user = User.create(telegram_id=TelegramID(123456789))
        mock_user_service.get_or_create_user.return_value = user
        
        # Create callback handler
        callback_handlers = CallbackHandlers()
        
        # Act
        await callback_handlers.handle_callback_query(mock_update, mock_context)
        
        # Assert
        mock_update.callback_query.answer.assert_called()
    
    async def test_help_command(
        self,
        bot_application,
        mock_telegram_update,
        mock_telegram_context,
        mock_container
    ):
        """Test help command."""
        # Arrange
        mock_telegram_update.message.text = "/help"
        
        # Create command handler
        command_handlers = CommandHandlers()
        
        # Act
        await command_handlers.help_command(mock_telegram_update, mock_telegram_context)
        
        # Assert
        mock_telegram_context.bot.send_message.assert_called()
        
        # Check that help message was sent
        send_message_call = mock_telegram_context.bot.send_message.call_args
        message_text = send_message_call[1]["text"]
        assert "help" in message_text.lower() or "command" in message_text.lower()
    
    async def test_recent_command(
        self,
        bot_application,
        mock_telegram_update,
        mock_telegram_context,
        mock_container
    ):
        """Test recent decodes command."""
        # Arrange
        mock_telegram_update.message.text = "/recent"
        
        # Mock user service
        mock_user_service = AsyncMock()
        mock_container.user_application_service.return_value = mock_user_service
        
        from src.domain.user.entities.user import User, UserHistory
        from src.domain.user.value_objects.telegram_id import TelegramID
        
        user = User.create(telegram_id=TelegramID(123456789))
        
        # Add some history
        history = [
            UserHistory(
                vin="1HGBH41JXMN109186",
                service_used="nhtsa",
                vehicle_info={"make": "Honda", "model": "Civic"},
                decoded_at=datetime.utcnow()
            )
        ]
        user.history = history
        
        mock_user_service.get_or_create_user.return_value = user
        mock_user_service.get_user_recent_history.return_value = history
        
        # Create command handler
        command_handlers = CommandHandlers()
        
        # Act
        await command_handlers.recent_command(mock_telegram_update, mock_telegram_context)
        
        # Assert
        mock_telegram_context.bot.send_message.assert_called()
        
        # Check that recent history was sent
        send_message_call = mock_telegram_context.bot.send_message.call_args
        message_text = send_message_call[1]["text"]
        assert "Honda" in message_text or "recent" in message_text.lower()
    
    async def test_saved_command(
        self,
        bot_application,
        mock_telegram_update,
        mock_telegram_context,
        mock_container
    ):
        """Test saved vehicles command."""
        # Arrange
        mock_telegram_update.message.text = "/saved"
        
        # Mock user service
        mock_user_service = AsyncMock()
        mock_container.user_application_service.return_value = mock_user_service
        
        from src.domain.user.entities.user import User
        from src.domain.user.value_objects.telegram_id import TelegramID
        
        user = User.create(telegram_id=TelegramID(123456789))
        user.saved_vehicles = ["1HGBH41JXMN109186"]
        
        mock_user_service.get_or_create_user.return_value = user
        
        # Create command handler
        command_handlers = CommandHandlers()
        
        # Act
        await command_handlers.saved_command(mock_telegram_update, mock_telegram_context)
        
        # Assert
        mock_telegram_context.bot.send_message.assert_called()
        
        # Check that saved vehicles were sent
        send_message_call = mock_telegram_context.bot.send_message.call_args
        message_text = send_message_call[1]["text"]
        assert "1HGBH41JXMN109186" in message_text or "saved" in message_text.lower()
    
    async def test_error_handling_in_commands(
        self,
        bot_application,
        mock_telegram_update,
        mock_telegram_context,
        mock_container
    ):
        """Test error handling in bot commands."""
        # Arrange
        mock_telegram_update.message.text = "/vin 1HGBH41JXMN109186"
        
        # Mock user service to raise an exception
        mock_user_service = AsyncMock()
        mock_user_service.get_or_create_user.side_effect = Exception("Database error")
        mock_container.user_application_service.return_value = mock_user_service
        
        # Create command handler
        command_handlers = CommandHandlers()
        
        # Act
        await command_handlers.vin_command(mock_telegram_update, mock_telegram_context)
        
        # Assert
        mock_telegram_context.bot.send_message.assert_called()
        
        # Check that error message was sent
        send_message_call = mock_telegram_context.bot.send_message.call_args
        message_text = send_message_call[1]["text"]
        assert "error" in message_text.lower() or "sorry" in message_text.lower()
    
    async def test_bot_application_lifecycle(
        self,
        mock_container,
        mock_telegram_application
    ):
        """Test bot application startup and shutdown."""
        # Arrange
        with patch('telegram.ext.Application.builder') as mock_builder:
            mock_builder.return_value.token.return_value.build.return_value = mock_telegram_application
            
            bot_app = BotApplication()
            bot_app.container = mock_container
            
            # Act - Start
            await bot_app.run()
            
            # Assert startup
            mock_telegram_application.initialize.assert_called_once()
            mock_telegram_application.start.assert_called_once()
            mock_telegram_application.updater.start_polling.assert_called_once()
            
            # Act - Shutdown
            await bot_app.shutdown()
            
            # Assert shutdown
            mock_telegram_application.updater.stop.assert_called_once()
            mock_telegram_application.stop.assert_called_once()
            mock_telegram_application.shutdown.assert_called_once()
    
    async def test_bot_message_formatting(
        self,
        bot_application,
        mock_telegram_update,
        mock_telegram_context,
        mock_container
    ):
        """Test that bot formats messages correctly."""
        # Arrange
        test_vin = "1HGBH41JXMN109186"
        mock_telegram_update.message.text = f"/vin {test_vin}"
        
        # Mock services
        mock_user_service = AsyncMock()
        mock_vehicle_service = AsyncMock()
        mock_container.user_application_service.return_value = mock_user_service
        mock_container.vehicle_application_service.return_value = mock_vehicle_service
        
        from src.domain.user.entities.user import User
        from src.domain.user.value_objects.telegram_id import TelegramID
        from src.domain.vehicle.value_objects.decode_result import DecodeResult
        from src.domain.vehicle.value_objects.vin_number import VINNumber
        
        user = User.create(telegram_id=TelegramID(123456789))
        mock_user_service.get_or_create_user.return_value = user
        
        decode_result = DecodeResult(
            vin=VINNumber(test_vin),
            success=True,
            data={
                "make": "Honda",
                "model": "Civic",
                "year": 2021,
                "body_type": "Sedan",
                "engine": "1.5L 4-Cylinder"
            },
            service_used="nhtsa"
        )
        mock_vehicle_service.decode_vin.return_value = decode_result
        
        # Create command handler
        command_handlers = CommandHandlers()
        
        # Act
        await command_handlers.vin_command(mock_telegram_update, mock_telegram_context)
        
        # Assert
        mock_telegram_context.bot.send_message.assert_called()
        
        # Check message formatting
        send_message_call = mock_telegram_context.bot.send_message.call_args
        message_text = send_message_call[1]["text"]
        
        # Should contain vehicle information
        assert "Honda" in message_text
        assert "Civic" in message_text
        assert "2021" in message_text
        assert "Sedan" in message_text
        
        # Should have proper formatting (bold VIN, etc.)
        assert test_vin in message_text

