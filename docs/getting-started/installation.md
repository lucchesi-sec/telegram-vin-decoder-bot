# IntelAuto Installation Guide

This guide covers installation options for IntelAuto, from development setup to production deployment.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Node.js 18+ (for web dashboard)
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (recommended)

### Quick Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/telegram-vin-decoder-bot.git
   cd telegram-vin-decoder-bot
   ```

2. **Set up environment**
   ```bash
   cp config/.env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose -f config/docker-compose.yml up -d
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

5. **Run database migrations**
   ```bash
   alembic -c config/alembic.ini upgrade head
   ```

6. **Start the application**
   ```bash
   # Start the API server
   python start_api_server.py
   
   # Start the Telegram bot (in another terminal)
   python main.py
   ```

## Production Deployment

### Option 1: Fly.io (Recommended)

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy**
   ```bash
   fly deploy --config config/fly.toml
   ```

### Option 2: Docker Deployment

1. **Build the image**
   ```bash
   docker build -t intellauto:latest .
   ```

2. **Run with docker-compose**
   ```bash
   docker-compose -f config/docker-compose.yml -f config/docker-compose.prod.yml up -d
   ```

### Option 3: Manual Deployment

See [Deployment Guide](../technical/deployment.md) for detailed production setup instructions.

## Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/intellauto

# Redis
REDIS_URL=redis://localhost:6379

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook

# API Keys
NHTSA_API_KEY=your_nhtsa_key
AUTODEV_API_KEY=your_autodev_key

# Security
JWT_SECRET_KEY=your_jwt_secret
API_RATE_LIMIT=100
```

See [Configuration Guide](../configuration.md) for complete variable reference.

## Verification

### Test the Installation

1. **API Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Run Test Suite**
   ```bash
   pytest
   ```

3. **Test VIN Decoding**
   ```bash
   curl -X POST "http://localhost:8000/v1/vin/decode" \
     -H "Content-Type: application/json" \
     -d '{"vin": "1HGBH41JXMN109186"}'
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure database exists

2. **Redis Connection Failed**
   - Check Redis is running
   - Verify REDIS_URL in .env

3. **Telegram Webhook Issues**
   - Ensure TELEGRAM_WEBHOOK_URL is accessible
   - Check SSL certificate validity

### Getting Help

- 📚 Check the [Technical Documentation](../technical/)
- 🐛 Report issues on [GitHub](https://github.com/yourusername/telegram-vin-decoder-bot/issues)
- 💬 Join our community for support

## Next Steps

- 📖 Read the [Quick Start Guide](quick-start.md)
- 🔧 Configure your [Environment Variables](../configuration.md)
- 🚀 Explore the [API Documentation](../user-guides/api-usage.md)
