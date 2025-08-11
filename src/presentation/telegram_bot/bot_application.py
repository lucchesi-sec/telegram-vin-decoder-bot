"""Main bot application."""

import asyncio
import logging
from typing import Optional
from dependency_injector.wiring import inject, Provide
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from src.infrastructure.monitoring.logging_config import setup_logging
from src.config.settings import Settings
from src.config.dependencies import Container
from src.presentation.telegram_bot.handlers.command_handlers import CommandHandlers
from src.presentation.telegram_bot.handlers.callback_handlers import CallbackHandlers
from src.application.vehicle.services.vehicle_application_service import VehicleApplicationService
from src.application.user.services.user_application_service import UserApplicationService
from src.presentation.telegram_bot.adapters.message_adapter import MessageAdapter
from src.presentation.telegram_bot.adapters.keyboard_adapter import KeyboardAdapter

logger = logging.getLogger(__name__)


class BotApplication:
    """Main bot application class."""
    
    @inject
    def __init__(
        self,
        settings: Settings = Provide[Container.settings],
        vehicle_service: VehicleApplicationService = Provide[Container.vehicle_application_service],
        user_service: UserApplicationService = Provide[Container.user_application_service],
        message_adapter: MessageAdapter = Provide[Container.message_adapter],
        keyboard_adapter: KeyboardAdapter = Provide[Container.keyboard_adapter]
    ):
        """Initialize the bot application.
        
        Args:
            settings: Application settings
            vehicle_service: Vehicle application service
            user_service: User application service
            message_adapter: Message formatting adapter
            keyboard_adapter: Keyboard creation adapter
        """
        self.settings = settings
        self.vehicle_service = vehicle_service
        self.user_service = user_service
        self.message_adapter = message_adapter
        self.keyboard_adapter = keyboard_adapter
        self.application = None
        self.stop_event: Optional[asyncio.Event] = None
        self.command_handlers = None
        self.callback_handlers = None
    
    async def initialize(self) -> None:
        """Initialize the bot application."""
        try:
            # Set up logging
            logger.info("Setting up logging...")
            setup_logging(self.settings.log_level)
            
            # Create application
            logger.info("Creating Telegram application...")
            bot_token = self.settings.telegram.bot_token.get_secret_value()
            logger.info(f"Bot token length: {len(bot_token)} characters")
            
            self.application = (
                ApplicationBuilder()
                .token(bot_token)
                .build()
            )
            logger.info("Telegram application created successfully")
            
            # Create handler instances with injected services and adapters
            logger.info("Creating command handlers...")
            self.command_handlers = CommandHandlers(
                vehicle_service=self.vehicle_service,
                user_service=self.user_service,
                message_adapter=self.message_adapter,
                keyboard_adapter=self.keyboard_adapter
            )
            
            logger.info("Creating callback handlers...")
            self.callback_handlers = CallbackHandlers(
                vehicle_service=self.vehicle_service,
                user_service=self.user_service,
                message_adapter=self.message_adapter,
                keyboard_adapter=self.keyboard_adapter
            )
            
            # Set up handlers
            logger.info("Setting up handlers...")
            await self._setup_handlers()
            
            logger.info("Bot application initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing bot application: {e}", exc_info=True)
            raise
    
    async def _setup_handlers(self) -> None:
        """Set up command and callback handlers."""
        # Register command handlers
        self.application.add_handler(CommandHandler("start", self.command_handlers.start))
        self.application.add_handler(CommandHandler("help", self.command_handlers.help))
        self.application.add_handler(CommandHandler("vin", self.command_handlers.vin))
        self.application.add_handler(CommandHandler("settings", self.command_handlers.settings))
        self.application.add_handler(CommandHandler("history", self.command_handlers.history))
        
        # Register callback handler
        self.application.add_handler(CallbackQueryHandler(self.callback_handlers.handle_callback))
        
        # Register message handler for direct VIN input
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text_message)
        )
        
        logger.info("Handlers set up successfully")
    
    async def _handle_text_message(self, update, context) -> None:
        """Handle direct text messages (potential VINs)."""
        try:
            if not update.message or not update.message.text:
                return
            
            text = update.message.text.strip()
            
            # Check if it looks like a VIN (17 characters)
            if len(text) == 17 and text.isalnum():
                # Pass to the VIN handler
                context.args = [text]
                await self.command_handlers.vin(update, context)
            else:
                # Check if this is a settings-related input (e.g., API key)
                if hasattr(context, 'user_data') and context.user_data.get('awaiting_api_key'):
                    # Handle API key input
                    await self.callback_handlers.handle_api_key_input(update, context, text)
                else:
                    await update.message.reply_text(
                        "I expected a 17-character VIN. Use /vin <VIN> or send the VIN directly."
                    )
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )
    
    def run(self) -> None:
        """Run the bot application (synchronous version)."""
        try:
            if not self.application:
                logger.info("Initializing bot application...")
                # We need to run initialize in a sync context
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.initialize())
                loop.close()
            
            logger.info("Starting bot polling...")
            # Test bot connection first
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                bot_info = loop.run_until_complete(self.application.bot.get_me())
                logger.info(f"Bot connected successfully: @{bot_info.username} ({bot_info.first_name})")
                loop.close()
            except Exception as e:
                logger.error(f"Failed to connect to Telegram API: {e}")
                raise
            
            logger.info("Starting bot with run_polling...")
            # Use run_polling which handles its own event loop
            self.application.run_polling(
                allowed_updates=None,
                drop_pending_updates=True,
                stop_signals=None  # Let the main process handle signals
            )
            
            logger.info("Bot polling stopped")
        except Exception as e:
            logger.error(f"Error running bot application: {e}", exc_info=True)
            raise
    
    def shutdown(self) -> None:
        """Shutdown the bot application."""
        try:
            logger.info("Shutting down bot application...")
            
            if self.application:
                # The application should handle its own shutdown when run_polling stops
                logger.info("Bot application will shut down automatically")
                
            logger.info("Bot application shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down bot application: {e}")


@inject
def create_bot_application(
    settings: Settings = Provide[Container.settings],
    vehicle_service: VehicleApplicationService = Provide[Container.vehicle_application_service],
    user_service: UserApplicationService = Provide[Container.user_application_service],
    message_adapter: MessageAdapter = Provide[Container.message_adapter],
    keyboard_adapter: KeyboardAdapter = Provide[Container.keyboard_adapter]
) -> BotApplication:
    """Factory function to create bot application with dependency injection.
    
    Args:
        settings: Application settings
        vehicle_service: Vehicle application service
        user_service: User application service
        message_adapter: Message formatting adapter
        keyboard_adapter: Keyboard creation adapter
        
    Returns:
        Configured BotApplication instance
    """
    return BotApplication(settings, vehicle_service, user_service, message_adapter, keyboard_adapter)