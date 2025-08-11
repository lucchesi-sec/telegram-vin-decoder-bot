"""Main entry point for the application."""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.dependencies import Container
from src.config.validation import check_startup_requirements, print_environment_info
from src.presentation.telegram_bot.bot_application import BotApplication
from src.infrastructure.monitoring.http_health import HealthCheckServer

logger = logging.getLogger(__name__)


async def main():
    """Main application entry point."""
    health_server = None
    bot_app = None
    
    try:
        # Set up basic logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )
        
        # Start health check server for Fly.io smoke tests (in daemon thread)
        health_server = HealthCheckServer(port=8080)
        health_server.start()
        
        # Print environment info for debugging
        print_environment_info()
        
        # Check startup requirements
        if not check_startup_requirements():
            logger.error("Startup requirements not met. Exiting.")
            return False
        
        # Create dependency injection container
        logger.info("Creating dependency injection container...")
        container = Container()
        
        # Wire the container to all modules that use dependency injection
        logger.info("Wiring dependency injection container...")
        container.wire(modules=[
            "src.presentation.telegram_bot.bot_application",
            "src.presentation.telegram_bot.handlers.command_handlers",
            "src.presentation.telegram_bot.handlers.callback_handlers"
        ])
        
        # Create bot application with dependency injection
        logger.info("Creating bot application...")
        bot_app = BotApplication()
        
        # Run the bot - this will block until shutdown
        logger.info("Starting bot application...")
        await bot_app.run()
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        return True
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return False
    finally:
        # Clean shutdown
        logger.info("Cleaning up resources...")
        
        if bot_app:
            try:
                await bot_app.shutdown()
                logger.info("Bot application shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down bot: {e}")
        
        if health_server:
            try:
                health_server.stop()
                logger.info("Health server stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping health server: {e}")


if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )
    
    # Set up signal handlers for graceful shutdown
    def handle_sigterm(signum, frame):
        logger.info("Received SIGTERM, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)
    
    # Run the application
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        logger.info(f"Application finished with exit code: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)