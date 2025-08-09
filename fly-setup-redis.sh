#!/bin/bash

# Script to set up Redis for VIN Bot on Fly.io

echo "Setting up Redis for VIN Bot on Fly.io..."

# Create Redis instance
echo "Creating Redis instance..."
fly redis create --name vinbot-redis --region ewr --plan Free

# Get Redis connection URL
echo "Getting Redis connection URL..."
REDIS_URL=$(fly redis status vinbot-redis --json | jq -r '.instances[0].private_url')

# Set Redis URL as a secret in the main app
echo "Setting Redis URL as secret in vinbot-decoder app..."
fly secrets set REDIS_URL="redis://$REDIS_URL" --app vinbot-decoder

echo "Redis setup complete!"
echo "Redis instance: vinbot-redis"
echo "Connection will be available via REDIS_URL environment variable"