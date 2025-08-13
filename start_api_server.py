#!/usr/bin/env python3
"""Start the new modular API server."""

import uvicorn
from src.presentation.api.server import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)