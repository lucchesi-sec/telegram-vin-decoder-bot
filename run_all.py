#!/usr/bin/env python3
"""Run both the Telegram bot and web dashboard."""

import asyncio
import sys
import logging
from pathlib import Path
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

logger = logging.getLogger(__name__)


def run_bot():
    """Run the Telegram bot."""
    from src.main import main
    asyncio.run(main())


def run_dashboard():
    """Run the web dashboard."""
    import uvicorn
    from src.config.dependencies import Container
    
    container = Container()
    container.wire(modules=[
        "src.presentation.web_dashboard.api.vehicle_endpoints"
    ])
    
    asyncio.run(Container.initialize_database(container))
    Container.bootstrap(container)
    
    uvicorn.run(
        "src.presentation.web_dashboard.app:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


def main():
    """Run both services."""
    logger.info("Starting VIN Decoder services...")
    
    # Create processes for each service
    bot_process = multiprocessing.Process(target=run_bot, name="telegram-bot")
    dashboard_process = multiprocessing.Process(target=run_dashboard, name="web-dashboard")
    
    try:
        # Start both processes
        bot_process.start()
        dashboard_process.start()
        
        logger.info("✅ Telegram bot started")
        logger.info("✅ Web dashboard started at http://localhost:8000")
        logger.info("Press Ctrl+C to stop both services")
        
        # Wait for both processes
        bot_process.join()
        dashboard_process.join()
        
    except KeyboardInterrupt:
        logger.info("Shutting down services...")
        bot_process.terminate()
        dashboard_process.terminate()
        bot_process.join()
        dashboard_process.join()
        logger.info("Services stopped")


if __name__ == "__main__":
    main()