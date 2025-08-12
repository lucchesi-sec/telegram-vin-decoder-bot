"""Main bot application."""

import asyncio
import logging
from typing import Optional

from dependency_injector.wiring import Provide, inject
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.application.user.services.user_application_service import (
    UserApplicationService,
)
from src.application.vehicle.services.vehicle_application_service import (
    VehicleApplicationService,
)
from src.config.dependencies import Container
from src.config.settings import Settings
from src.infrastructure.monitoring.logging_config import setup_logging
from src.presentation.telegram_bot.adapters.keyboard_adapter import KeyboardAdapter
from src.presentation.telegram_bot.adapters.message_adapter import MessageAdapter
from src.presentation.telegram_bot.handlers.callback_handlers import CallbackHandlers
from src.presentation.telegram_bot.handlers.command_handlers import CommandHandlers
from src.presentation.telegram_bot.utils.vin_validator import VINValidator
from src.infrastructure.persistence.cache.message_cache import MessageCache

logger = logging.getLogger(__name__)


class BotApplication:
    """Main bot application class."""

    @inject
    def __init__(
        self,
        settings: Settings = Provide[Container.settings],
        vehicle_service: VehicleApplicationService = Provide[
            Container.vehicle_application_service
        ],
        user_service: UserApplicationService = Provide[
            Container.user_application_service
        ],
        message_adapter: MessageAdapter = Provide[Container.message_adapter],
        keyboard_adapter: KeyboardAdapter = Provide[Container.keyboard_adapter],
        message_cache: Optional[MessageCache] = Provide[Container.message_cache],
    ):
        """Initialize the bot application.

        Args:
            settings: Application settings
            vehicle_service: Vehicle application service
            user_service: User application service
            message_adapter: Message formatting adapter
            keyboard_adapter: Keyboard creation adapter
            message_cache: Optional message cache for performance
        """
        self.settings = settings
        self.vehicle_service = vehicle_service
        self.user_service = user_service
        self.message_adapter = message_adapter
        self.keyboard_adapter = keyboard_adapter
        self.message_cache = message_cache
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

            self.application = ApplicationBuilder().token(bot_token).build()
            logger.info("Telegram application created successfully")

            # Create handler instances with injected services and adapters
            logger.info("Creating command handlers...")
            self.command_handlers = CommandHandlers(
                vehicle_service=self.vehicle_service,
                user_service=self.user_service,
                message_adapter=self.message_adapter,
                keyboard_adapter=self.keyboard_adapter,
                message_cache=self.message_cache,
            )

            logger.info("Creating callback handlers...")
            self.callback_handlers = CallbackHandlers(
                vehicle_service=self.vehicle_service,
                user_service=self.user_service,
                message_adapter=self.message_adapter,
                keyboard_adapter=self.keyboard_adapter,
                message_cache=self.message_cache,
            )

            # Set up handlers
            logger.info("Setting up handlers...")
            await self._setup_handlers()

            # Set bot commands for slash command suggestions
            logger.info("Setting up bot commands...")
            await self._set_bot_commands()

            logger.info("Bot application initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing bot application: {e}", exc_info=True)
            raise

    async def _setup_handlers(self) -> None:
        """Set up command and callback handlers."""
        # Register command handlers
        self.application.add_handler(
            CommandHandler("start", self.command_handlers.start)
        )
        self.application.add_handler(CommandHandler("help", self.command_handlers.help))
        self.application.add_handler(CommandHandler("vin", self.command_handlers.vin))
        self.application.add_handler(
            CommandHandler("settings", self.command_handlers.settings)
        )
        self.application.add_handler(
            CommandHandler("history", self.command_handlers.history)
        )

        # Register callback handler
        self.application.add_handler(
            CallbackQueryHandler(self.callback_handlers.handle_callback)
        )

        # Register message handler for direct VIN input
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text_message)
        )

        logger.info("Handlers set up successfully")

    async def _set_bot_commands(self) -> None:
        """Set bot commands for slash command suggestions."""
        from telegram import BotCommand

        commands = [
            BotCommand("start", "Show welcome message and options"),
            BotCommand("vin", "Decode a VIN number"),
            BotCommand("settings", "Configure decoder service and API keys"),
            BotCommand("history", "View your recent VIN searches"),
            BotCommand("help", "Show help and available commands"),
        ]

        try:
            await self.application.bot.set_my_commands(commands)
            logger.info("Bot commands set successfully")
        except Exception as e:
            logger.error(f"Error setting bot commands: {e}")

    async def _handle_text_message(self, update, context) -> None:
        """Handle direct text messages (potential VINs)."""
        try:
            if not update.message or not update.message.text:
                return

            text = update.message.text.strip()

            # Try to extract VIN from the text
            extracted_vin = VINValidator.extract_vin(text)

            if extracted_vin:
                # Valid VIN found! Automatically decode it
                logger.info(f"Auto-detected VIN: {extracted_vin}")

                # Pass to the VIN handler directly without a processing message
                # to avoid duplicate messages
                context.args = [extracted_vin]
                await self.command_handlers.vin(update, context)

            elif VINValidator.looks_like_vin_attempt(text):
                # User seems to be trying to enter a VIN but it's invalid
                await update.message.reply_text(
                    "❌ That looks like a VIN, but it's not valid.\n\n"
                    "VINs must be exactly 17 characters and cannot contain I, O, or Q.\n"
                    "Please check and try again."
                )
            else:
                # Not a VIN - provide helpful guidance
                await update.message.reply_text(
                    "💡 Send me a 17-character VIN to decode it automatically!\n\n"
                    "You can also use:\n"
                    "• /vin <VIN> to decode a specific VIN\n"
                    "• /help for more commands"
                )
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )

    async def run_async(self) -> None:
        """Run the bot application (async version)."""
        try:
            if not self.application:
                logger.info("Initializing bot application...")
                await self.initialize()

            logger.info("Starting bot polling...")
            # Test bot connection first
            try:
                bot_info = await self.application.bot.get_me()
                logger.info(
                    f"Bot connected successfully: @{bot_info.username} ({bot_info.first_name})"
                )
            except Exception as e:
                logger.error(f"Failed to connect to Telegram API: {e}")
                raise

            logger.info("Starting bot with initialize and start...")
            # Initialize and start the application
            await self.application.initialize()
            await self.application.start()

            # Start polling
            logger.info("Starting bot polling...")
            await self.application.updater.start_polling(
                allowed_updates=None, drop_pending_updates=True
            )

            # Keep the bot running
            logger.info("Bot is now running. Waiting for stop signal...")
            self.stop_event = asyncio.Event()
            await self.stop_event.wait()

            # Stop polling
            logger.info("Stopping bot polling...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

            logger.info("Bot polling stopped")
        except Exception as e:
            logger.error(f"Error running bot application: {e}", exc_info=True)
            raise

    def run(self) -> None:
        """Run the bot application (synchronous version for backward compatibility)."""
        try:
            # Check if we're already in an async context
            try:
                _ = asyncio.get_running_loop()
                # If there's already a loop, we can't use asyncio.run()
                logger.error(
                    "Cannot call run() from within an async context. Use run_async() instead."
                )
                raise RuntimeError("Cannot call run() from within an async context")
            except RuntimeError:
                # No running loop, safe to use asyncio.run()
                asyncio.run(self.run_async())
        except Exception as e:
            logger.error(f"Error running bot application: {e}", exc_info=True)
            raise

    def shutdown(self) -> None:
        """Shutdown the bot application."""
        try:
            logger.info("Shutting down bot application...")

            if self.stop_event:
                # Signal the async run to stop
                self.stop_event.set()

            if self.application:
                # The application should handle its own shutdown when run_polling stops
                logger.info("Bot application will shut down automatically")

            logger.info("Bot application shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down bot application: {e}")


@inject
def create_bot_application(
    settings: Settings = Provide[Container.settings],
    vehicle_service: VehicleApplicationService = Provide[
        Container.vehicle_application_service
    ],
    user_service: UserApplicationService = Provide[Container.user_application_service],
    message_adapter: MessageAdapter = Provide[Container.message_adapter],
    keyboard_adapter: KeyboardAdapter = Provide[Container.keyboard_adapter],
    message_cache: Optional[MessageCache] = Provide[Container.message_cache],
) -> BotApplication:
    """Factory function to create bot application with dependency injection.

    Args:
        settings: Application settings
        vehicle_service: Vehicle application service
        user_service: User application service
        message_adapter: Message formatting adapter
        keyboard_adapter: Keyboard creation adapter
        message_cache: Optional message cache for performance

    Returns:
        Configured BotApplication instance
    """
    return BotApplication(
        settings, vehicle_service, user_service, message_adapter, keyboard_adapter, message_cache
    )
