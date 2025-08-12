#!/bin/sh
set -e

echo "Starting FastAPI server..."
cd /app
python -m uvicorn src.presentation.api.api_server:app --host 0.0.0.0 --port 5000 &
API_PID=$!

echo "Starting web dashboard..."
cd /app/web-dashboard-next
export PORT=8000
export HOSTNAME=0.0.0.0
export BACKEND_URL=http://localhost:5000

npm run start &
WEB_PID=$!

wait $API_PID $WEB_PID