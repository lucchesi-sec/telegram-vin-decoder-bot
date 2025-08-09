# Telegram VIN Decoder Bot (CarsXE)

A Telegram bot that takes a VIN, decodes it using the CarsXE API, and returns detailed vehicle information.

## Features
- Accepts VIN via command or plain message
- Validates VIN format before calling the API
- Fetches decoded details from CarsXE (async HTTP)
- Formats a readable vehicle summary
- Config via environment variables
- Optional Docker support

## Prerequisites
- Python 3.9+
- Telegram Bot Token from @BotFather
- CarsXE API key (https://www.carsxe.com/)

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
# edit .env to add TELEGRAM_BOT_TOKEN and CARSXE_API_KEY
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

You can also just send a plain 17-character VIN and the bot will decode it.

## Configuration
Environment variables (via `.env`):
- `TELEGRAM_BOT_TOKEN`: Telegram bot token from @BotFather
- `CARSXE_API_KEY`: CarsXE API key
- `HTTP_TIMEOUT_SECONDS` (optional): HTTP client timeout in seconds (default 15)
- `LOG_LEVEL` (optional): INFO, DEBUG, etc.

## CarsXE API Notes
This bot targets the CarsXE VIN Decode endpoint, typically `https://api.carsxe.com/vin` with query params `key` and `vin`. If your plan or endpoint differs, adjust `VIN_ENDPOINT` in `vinbot/carsxe_client.py` accordingly.

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
    ├── carsxe_client.py
    ├── config.py
    ├── formatter.py
    └── vin.py
```

## Development
- Lint/format tools are not included by default; feel free to add `ruff`/`black`.
- To run in debug logging, set `LOG_LEVEL=DEBUG` in `.env`.

## Disclaimer
This is a starter scaffold. Confirm your CarsXE plan and endpoint parameters and tune the field mapping in `formatter.py` based on the actual response payload you receive.
