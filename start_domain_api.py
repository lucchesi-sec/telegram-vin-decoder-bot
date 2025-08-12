#!/usr/bin/env python
"""Start the domain-driven API server."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from src.presentation.api.domain_api_server import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5001,
        log_level="info",
        reload=False
    )