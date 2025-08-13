#!/bin/sh
set -e

echo "Running database migrations..."
max_retries=5
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if alembic upgrade head; then
        echo "Migrations completed successfully"
        break
    else
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            wait_time=$((1 << retry_count))
            echo "Migration attempt $retry_count failed, retrying in ${wait_time}s..."
            sleep $wait_time
        else
            echo "All migration attempts failed after $max_retries tries"
            exit 1
        fi
    fi
done

echo "Starting bot..."
exec python -m src.main