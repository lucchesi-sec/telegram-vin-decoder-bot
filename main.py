#!/usr/bin/env python3
"""Legacy entry point retained for compatibility; forwards to src/main.py."""

import logging
import sys
from pathlib import Path


def _forward_to_src_main() -> int:
    sys.path.insert(0, str(Path(__file__).parent))
    from src.main import main  # type: ignore
    import asyncio
    asyncio.run(main())
    return 0


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

if __name__ == "__main__":
    try:
        raise SystemExit(_forward_to_src_main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Bot crashed: {e}")
        sys.exit(1)