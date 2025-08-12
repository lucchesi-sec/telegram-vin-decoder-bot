#!/bin/sh
set -e

echo "Starting FastAPI server..."
cd /app
exec python -m uvicorn src.presentation.api.api_server:app --host 0.0.0.0 --port 5000