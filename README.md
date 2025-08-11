# Telegram VIN Decoder Bot

A Telegram bot that takes a VIN, decodes it using either the free NHTSA API or the premium Auto.dev API, and returns detailed vehicle information.

## Features
- Accepts VIN via command or plain message
- Validates VIN format before calling the API
- Fetches decoded details from NHTSA (free) or Auto.dev (premium)
- Formats a readable vehicle summary
- Config via environment variables
- Optional Docker support
- User settings to switch between services (NHTSA or Auto.dev)
- API key management for premium services (Auto.dev)

## Prerequisites
- Python 3.9+
- Telegram Bot Token from @BotFather
- Auto.dev API key (optional, https://auto.dev/)

## Quick Start

1. Clone this repo and enter the folder, then set up a virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create your `.env` based on the example:

```bash
cp .env.example .env
# edit .env to add TELEGRAM_BOT_TOKEN
```

3. Run the bot:

```bash
python -m vinbot
```

The bot starts polling. In Telegram, send your bot a message with a 17-character VIN (e.g. `/vin 1HGCM82633A004352`).

## Commands
- `/start` — brief intro and instructions
- `/help` — usage help
- `/vin <VIN>` — decode a VIN directly
- `/settings` — configure service preferences and API keys
- `/recent` — view recent searches
- `/saved` — view saved vehicles

You can also just send a plain 17-character VIN and the bot will decode it.

## Services

### NHTSA (Default)
The bot uses the free NHTSA API by default, which provides basic vehicle information including:
- Make, model, and year
- Body type and vehicle type
- Engine specifications
- Manufacturing details

No API key is required for NHTSA.

### Auto.dev (Premium)
For more detailed vehicle information, you can switch to Auto.dev:
- Comprehensive vehicle specifications
- Detailed engine and transmission data
- Market value information
- Vehicle history (where available)
- Additional features and equipment

To use Auto.dev:
1. Get an API key from https://auto.dev/
2. Use the `/settings` command in the bot
3. Select "Auto.dev (Premium)"
4. Add your API key when prompted

## Configuration
Environment variables (via `.env`):
- `TELEGRAM_BOT_TOKEN`: Telegram bot token from @BotFather
- `HTTP_TIMEOUT_SECONDS` (optional): HTTP client timeout in seconds (default 15)
- `LOG_LEVEL` (optional): INFO, DEBUG, etc.
- `UPSTASH_REDIS_REST_URL` (optional): Upstash REST URL for caching
- `UPSTASH_REDIS_REST_TOKEN` (optional): Upstash REST token
- `REDIS_TTL_SECONDS` (optional): Cache TTL in seconds (default 86400)

## Docker
Build and run with Docker:

```bash
docker build -t vin-bot .
# Ensure .env is present. Then:
docker run --rm --env-file .env vin-bot
```

## Project Structure
```
.
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── Makefile
├── requirements.txt
└── vinbot/
    ├── __init__.py
    ├── bot.py
    ├── autodev_client.py
    ├── nhtsa_client.py
    ├── vin_decoder_base.py
    ├── config.py
    ├── formatter.py
    ├── keyboards.py
    ├── user_data.py
    └── vin.py
```

## Development
- Lint/format tools are not included by default; feel free to add `ruff`/`black`.
- To run in debug logging, set `LOG_LEVEL=DEBUG` in `.env`.
- For deployment on Fly.io, ensure `fly.toml` is properly configured with `auto_stop_machines`, `auto_start_machines`, and `min_machines_running` settings.

## Disclaimer
This is a starter scaffold. The field mapping in `formatter.py` may need to be adjusted based on the actual response payload you receive from the APIs.
