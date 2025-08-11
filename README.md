# Telegram VIN Decoder Bot (DDD Refactored)

A Telegram bot that decodes Vehicle Identification Numbers (VINs) using a Domain-Driven Design approach with clean architecture.

## Features

- **Automatic VIN Detection**: Just paste a VIN and the bot automatically detects and decodes it!
- Decodes VINs using official databases (NHTSA, Auto.dev)
- Domain-Driven Design with clear bounded contexts
- Clean architecture with separation of concerns
- Telegram bot interface with rich messaging
- Configurable services and API keys
- Comprehensive error handling
- Structured logging and monitoring
- Dependency injection for easy testing

## Architecture

This bot follows a Domain-Driven Design approach with clean architecture:

```
src/
├── domain/              # Domain layer with entities, value objects, and domain services
├── application/         # Application layer with use cases and business logic
├── infrastructure/      # Infrastructure layer with external service adapters
├── presentation/        # Presentation layer with Telegram bot interface
├── config/              # Configuration and dependency injection
└── tests/               # Unit, integration, and end-to-end tests
```

### Bounded Contexts

1. **Vehicle Domain**: Core VIN decoding, vehicle information management
2. **User Domain**: User preferences, history, subscription management
3. **Messaging Domain**: Telegram interaction, message formatting, UI components
4. **Integration Domain**: External API clients, third-party service adapters

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
python -m src.main
```

The bot starts polling. In Telegram, send your bot a message with a 17-character VIN (e.g. `/vin 1HGCM82633A004352`).

## Usage

### Automatic VIN Detection (NEW!)
Simply paste a VIN anywhere in your message and the bot will automatically detect and decode it:
- `1HGBH41JXMN109186` - Just the VIN
- `Check this VIN: 1HGBH41JXMN109186` - VIN in a sentence
- `Can you decode 1HGBH41JXMN109186 for me?` - Natural language

The bot intelligently detects 17-character VINs and validates them before decoding.

### Commands

- `/start` — Welcome message with interactive menu
- `/help` — Usage help and examples
- `/vin <VIN>` — Decode a VIN using the command
- `/settings` — View bot configuration
- `/history` — View your recent VIN searches

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
2. Add it to your `.env` file

## Configuration

Environment variables (via `.env`):
- `TELEGRAM_BOT_TOKEN`: Telegram bot token from @BotFather
- `AUTODEV_API_KEY`: Auto.dev API key (optional)
- `LOG_LEVEL`: INFO, DEBUG, etc.
- `DECODER_TIMEOUT`: HTTP client timeout in seconds (default 30)

## Development

- Lint/format tools are not included by default; feel free to add `ruff`/`black`.
- To run in debug logging, set `LOG_LEVEL=DEBUG` in `.env`.

## Testing

Run unit tests:
```bash
python -m pytest src/tests/unit
```

Run integration tests:
```bash
python -m pytest src/tests/integration
```

## Deployment

For deployment on any cloud platform, ensure your environment variables are properly configured.

## Project Structure

```
src/
├── domain/
│   ├── vehicle/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── events/
│   ├── user/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── repositories/
│   │   └── events/
│   └── shared/
├── application/
│   ├── vehicle/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── services/
│   ├── user/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── services/
│   └── shared/
├── infrastructure/
│   ├── persistence/
│   ├── external_services/
│   ├── messaging/
│   └── monitoring/
├── presentation/
│   ├── telegram_bot/
│   └── api/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
└── config/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.