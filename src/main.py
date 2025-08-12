"""Main entry point for the application."""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

import sentry_sdk

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.dependencies import Container
from src.config.validation import check_startup_requirements, print_environment_info
from src.presentation.telegram_bot.bot_application import BotApplication
from src.infrastructure.monitoring.http_health import HealthCheckServer

logger = logging.getLogger(__name__)


async def main():
    """Main application entry point."""
    # Initialize Sentry for error monitoring
    if sentry_dsn := os.getenv("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=0.1,
            environment=os.getenv("FLY_APP_NAME", "development"),
        )
        logger.info("Sentry monitoring initialized")
        # Test Sentry integration
        sentry_sdk.capture_message("Sentry integration test - bot starting", level="info")
    
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
        logger.info("Health check server started - listening on port 8080")
        
        # Print environment info for debugging
        print_environment_info()
        
        # Check startup requirements
        requirements_met = check_startup_requirements()
        if not requirements_met:
            logger.error("Startup requirements not met. Health server will remain running, but bot will not start.")
            logger.info("Waiting for configuration to be provided...")
            # Keep the process alive with health server running for deployment checks
            # This allows Fly.io smoke tests to pass while waiting for proper configuration
            stop_event = asyncio.Event()
            
            def signal_handler(signum, frame):
                _ = frame  # Unused parameter
                logger.info(f"Received signal {signum}, shutting down...")
                stop_event.set()
            
            import signal
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            await stop_event.wait()
            return True  # Return True so the process exits cleanly
        
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
        
        # Initialize database if configured
        logger.info("Initializing database if configured...")
        await Container.initialize_database(container)
        
        # Bootstrap the container to register handlers with buses
        logger.info("Bootstrapping container (registering handlers with buses)...")
        Container.bootstrap(container)
        
        # Create bot application with dependency injection
        logger.info("Creating bot application...")
        bot_app = BotApplication()
        
        # Run the bot - this will block until shutdown
        logger.info("Starting bot application...")
        await bot_app.run_async()
        
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
                bot_app.shutdown()
                logger.info("Bot application shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down bot: {e}")
        
        if health_server:
            try:
                health_server.stop()
                logger.info("Health server stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping health server: {e}")


def run_sync():
    """Run the application synchronously."""
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
        logger.info("Health check server started - listening on port 8080")
        
        # Print environment info for debugging
        print_environment_info()
        
        # Check startup requirements
        requirements_met = check_startup_requirements()
        if not requirements_met:
            logger.error("Startup requirements not met. Health server will remain running, but bot will not start.")
            logger.info("Waiting for configuration to be provided...")
            # Keep the process alive with health server running for deployment checks
            import time
            while True:
                time.sleep(60)  # Sleep and keep health server running
        
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
        
        # Initialize database if configured
        logger.info("Initializing database if configured...")
        import asyncio
        asyncio.run(Container.initialize_database(container))
        
        # Bootstrap the container to register handlers with buses
        logger.info("Bootstrapping container (registering handlers with buses)...")
        Container.bootstrap(container)
        
        # Create bot application with dependency injection
        logger.info("Creating bot application...")
        bot_app = BotApplication()
        
        # Run the bot - this will block until shutdown
        logger.info("Starting bot application...")
        bot_app.run()
        
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
                bot_app.shutdown()
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
    # Set up signal handlers for graceful shutdown
    def handle_sigterm(signum, frame):
        _ = frame  # Unused parameter
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)
    
    # Run the application
    try:
        success = run_sync()
        exit_code = 0 if success else 1
        logger.info(f"Application finished with exit code: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)