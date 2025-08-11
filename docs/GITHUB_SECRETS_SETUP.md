# GitHub Secrets Setup for Fly.io Deployment

## Required GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

### Core Secrets (Required)
- `FLY_API_TOKEN` - Your Fly.io API token
- `TELEGRAM_BOT_TOKEN` - Telegram bot token from BotFather
- `AUTODEV_API_KEY` - Auto.dev API key for VIN decoding

### Optional Services
- `CARSXE_API_KEY` - CarsXE API key (optional alternative decoder)
- `UPSTASH_REDIS_REST_URL` - Upstash Redis URL for caching
- `UPSTASH_REDIS_REST_TOKEN` - Upstash Redis authentication token

### Configuration
- `HTTP_TIMEOUT_SECONDS` - API timeout in seconds (default: 15)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)

## How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its name and value
5. The GitHub Action will automatically pass these to Fly.io during deployment

## Deployment

The workflow triggers automatically on:
- Push to `main` branch
- Manual trigger via GitHub Actions tab

All secrets are securely passed to Fly.io during deployment without being exposed in logs.