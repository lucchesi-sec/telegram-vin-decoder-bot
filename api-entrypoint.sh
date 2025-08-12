#!/bin/sh
set -e

echo "Starting Domain-Driven FastAPI server..."
cd /app
exec python -m uvicorn src.presentation.api.domain_api_server:app --host 0.0.0.0 --port 5000