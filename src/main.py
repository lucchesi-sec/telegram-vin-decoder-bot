"""Main entry point for the application."""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.dependencies import Container
from src.presentation.telegram_bot.bot_application import BotApplication

logger = logging.getLogger(__name__)


async def main():
    """Main application entry point."""
    bot_app = None
    try:
        # Create dependency injection container
        container = Container()
        
        # Wire the container to all modules that use dependency injection
        container.wire(modules=[
            "src.presentation.telegram_bot.bot_application",
            "src.presentation.telegram_bot.handlers.command_handlers",
            "src.presentation.telegram_bot.handlers.callback_handlers"
        ])
        
        # Create bot application with dependency injection
        bot_app = BotApplication()
        
        # Run the bot
        await bot_app.run()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if bot_app:
            await bot_app.shutdown()


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info('Shutting down gracefully...')
    # Create a task to stop the event loop
    asyncio.get_event_loop().stop()


if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )
    
    # Run the application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)