#!/usr/bin/env python3
"""
Main entry point for the Telegram VIN decoder bot.
"""

import logging
import sys
from vinbot.bot import main

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Bot crashed: {e}")
        sys.exit(1)