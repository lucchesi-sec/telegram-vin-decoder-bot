# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot that decodes Vehicle Identification Numbers (VINs) using the CarsXE API. The bot supports caching via Redis or Upstash, runs health checks for deployment on Fly.io, and provides vehicle information in a formatted response.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env to add TELEGRAM_BOT_TOKEN and CARSXE_API_KEY
```

### Running the Bot
```bash
# Local development
python -m vinbot
# or
make run

# Debug mode
LOG_LEVEL=DEBUG python -m vinbot
```

### Docker Commands
```bash
# Build Docker image
docker build -t vin-bot .
# or
make docker-build

# Run with Docker
docker run --rm --env-file .env vin-bot
# or
make docker-run
```

### Deployment to Fly.io
```bash
# Deploy (requires fly CLI)
fly deploy

# Set secrets
fly secrets set TELEGRAM_BOT_TOKEN=<token>
fly secrets set CARSXE_API_KEY=<key>
fly secrets set UPSTASH_REDIS_REST_URL=<url>  # Optional
fly secrets set UPSTASH_REDIS_REST_TOKEN=<token>  # Optional

# Check logs
fly logs

# Scale application
fly scale vm shared-cpu-1x
```

## Architecture

### Core Components

1. **Bot Module** (`vinbot/bot.py`):
   - Main Telegram bot implementation using python-telegram-bot
   - Handles commands: `/start`, `/help`, `/vin <VIN>`
   - Processes plain text VINs (17 characters)
   - Runs health check server on port 8080 for Fly.io monitoring
   - Manages graceful shutdown via signal handlers

2. **CarsXE Client** (`vinbot/carsxe_client.py`):
   - Async HTTP client for CarsXE API using httpx
   - Endpoint: `https://api.carsxe.com/specs`
   - Handles caching through injected cache interface
   - Error handling for API failures and invalid responses

3. **Caching Layer**:
   - **RedisCache** (`vinbot/redis_cache.py`): Standard Redis caching
   - **UpstashCache** (`vinbot/upstash_cache.py`): REST-based Upstash Redis
   - Cache priority: Upstash (if configured) > Redis (if configured) > No cache
   - Default TTL: 24 hours (configurable via `REDIS_TTL_SECONDS`)
   - Cache keys format: `vin:{VIN_UPPERCASE}`

4. **Configuration** (`vinbot/config.py`):
   - Environment-based configuration using python-dotenv
   - Required: `TELEGRAM_BOT_TOKEN`, `CARSXE_API_KEY`
   - Optional: `HTTP_TIMEOUT_SECONDS`, `LOG_LEVEL`, `REDIS_URL`, `REDIS_TTL_SECONDS`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`

5. **VIN Validation** (`vinbot/vin.py`):
   - Validates 17-character VINs
   - Excludes invalid characters (I, O, Q)
   - Normalizes VINs to uppercase

6. **Response Formatter** (`vinbot/formatter.py`):
   - Formats CarsXE API responses into human-readable summaries
   - Handles missing fields gracefully
   - Includes raw JSON in collapsible format

### Deployment Architecture

- **Platform**: Fly.io with shared CPU VM (1GB RAM)
- **Region**: Primary in `ewr` (US East)
- **Health Checks**: HTTP GET to `/health` every 30s
- **Process Management**: Single long-running bot process
- **Auto-rollback**: Enabled for failed deployments

## Key Implementation Details

### Async Patterns
- All API calls and bot handlers are async
- Health server runs in separate thread to avoid blocking
- Proper cleanup in `on_shutdown` handler

### Error Handling
- Custom `CarsXEError` for API-specific failures
- Graceful handling of network errors
- User-friendly error messages in Telegram

### Caching Strategy
- Check cache before API call
- Cache successful responses only
- Silent cache failures (fallback to API)
- Async cache operations for non-blocking behavior

## Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=          # From @BotFather
CARSXE_API_KEY=              # From carsxe.com

# Optional
HTTP_TIMEOUT_SECONDS=15      # API timeout
LOG_LEVEL=INFO               # INFO, DEBUG, ERROR
REDIS_URL=                   # redis://localhost:6379
REDIS_TTL_SECONDS=86400      # Cache TTL (24h default)
UPSTASH_REDIS_REST_URL=      # Upstash endpoint
UPSTASH_REDIS_REST_TOKEN=    # Upstash auth token
```

## Testing Strategies

While no formal tests exist, use these debug scripts for validation:
- `debug_carsxe.py` - Test CarsXE API directly
- `debug_bot_flow.py` - Test bot message flow
- `debug_with_cache.py` - Test caching behavior
- `debug_specific_vin.py` - Test specific VIN decoding

## Common Tasks

### Adding New Bot Commands
1. Add handler in `bot.py` (e.g., `CommandHandler("newcmd", cmd_newcmd)`)
2. Implement async handler function
3. Update `WELCOME_TEXT` with new command description

### Modifying Cache Behavior
1. Update cache implementation in `redis_cache.py` or `upstash_cache.py`
2. Adjust TTL via `REDIS_TTL_SECONDS` environment variable
3. Cache interface is consistent across both implementations

### Changing API Endpoint
1. Update `VIN_ENDPOINT` in `vinbot/carsxe_client.py`
2. Adjust response parsing in `decode_vin()` method
3. Update formatter in `vinbot/formatter.py` for new response structure

### Debugging Production Issues
```bash
# View live logs
fly logs

# SSH into container
fly ssh console

# Check environment
fly secrets list

# Monitor metrics
fly status
```