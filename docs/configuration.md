# Configuration Guide

This document provides comprehensive documentation for all environment variables used in the VIN Decoder Bot application.

## Overview

The application uses environment variables for configuration to maintain security and enable different configurations across environments (development, staging, production). All configuration values should be set in your `.env` file or environment.

## Quick Start

1. Copy `.env.example` to `.env`
2. Fill in the required values (marked with `*`)
3. Optional values have sensible defaults

```bash
cp .env.example .env
# Edit .env with your values
```

## Core Configuration

### Telegram Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Bot token from @BotFather |
| `TELEGRAM_WEBHOOK_URL` | ❌ | `None` | Webhook URL for production deployment |
| `TELEGRAM_MAX_CONNECTIONS` | ❌ | `40` | Maximum webhook connections |

**Example:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789
TELEGRAM_WEBHOOK_URL=https://your-app.fly.dev/webhook
```

### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ❌ | `None` | PostgreSQL connection string |
| `DB_POOL_SIZE` | ❌ | `20` | Database connection pool size |
| `DB_MAX_OVERFLOW` | ❌ | `10` | Maximum overflow connections |
| `DB_POOL_RECYCLE` | ❌ | `1800` | Connection recycle time (seconds) |
| `DB_POOL_PRE_PING` | ❌ | `true` | Test connections before use |
| `DB_POOL_TIMEOUT` | ❌ | `30` | Connection acquisition timeout |
| `DB_ECHO_SQL` | ❌ | `false` | Enable SQL query logging |

**Example:**
```bash
# Local development
DATABASE_URL=postgresql://postgres:secret@localhost:5432/vinbot

# Production (Fly.io automatically sets this)
DATABASE_URL=postgresql://username:password@hostname:5432/database
```

**Note:** If `DATABASE_URL` is not set, the application will use in-memory storage with automatic fallback.

### Cache Configuration (Upstash Redis)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `UPSTASH_REDIS_REST_URL` | ❌ | `None` | Upstash Redis REST API URL |
| `UPSTASH_REDIS_REST_TOKEN` | ❌ | `None` | Upstash Redis REST API token |
| `CACHE_TTL` | ❌ | `3600` | Default cache TTL (seconds) |
| `DECODER_CACHE_TTL` | ❌ | `2592000` | VIN decoder cache TTL (30 days) |
| `CACHE_TTL_SPECS` | ❌ | `86400` | Vehicle specs cache TTL (24 hours) |
| `CACHE_TTL_VALUATIONS` | ❌ | `3600` | Valuations cache TTL (1 hour) |
| `CACHE_TTL_HISTORY` | ❌ | `604800` | History cache TTL (7 days) |

**Example:**
```bash
UPSTASH_REDIS_REST_URL=https://your-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token_here
```

**Setup Guide:**
1. Create account at [Upstash Console](https://console.upstash.com/)
2. Create a new Redis database
3. Copy REST URL and token from dashboard
4. If not configured, application falls back to in-memory caching

## VIN Decoder Services

### AutoDev API (Recommended)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AUTODEV_API_KEY` | ✅ | - | API key from Auto.dev |
| `AUTODEV_BASE_URL` | ❌ | `https://api.auto.dev/` | AutoDev API base URL |
| `AUTODEV_TIMEOUT` | ❌ | `30000` | Request timeout (ms) |
| `AUTODEV_ENABLED` | ❌ | `true` | Enable AutoDev integration |

### NHTSA API (Free Alternative)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NHTSA_API_KEY` | ❌ | `None` | Optional NHTSA API key |
| `NHTSA_BASE_URL` | ❌ | `https://vpic.nhtsa.dot.gov/api/vehicles/` | NHTSA API base URL |
| `NHTSA_TIMEOUT` | ❌ | `30000` | Request timeout (ms) |
| `NHTSA_ENABLED` | ❌ | `true` | Enable NHTSA integration |

### Service Selection

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEFAULT_DECODER_SERVICE` | ❌ | `autodev` | Primary decoder service (`autodev` or `nhtsa`) |

**Example:**
```bash
AUTODEV_API_KEY=your_autodev_key_here
DEFAULT_DECODER_SERVICE=autodev
```

## Premium Services

### Manheim MMR (Market Value Reports)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MANHEIM_MMR_API_KEY` | ❌ | `None` | Manheim MMR API key |
| `MANHEIM_CLIENT_ID` | ❌ | `None` | OAuth client ID |
| `MANHEIM_CLIENT_SECRET` | ❌ | `None` | OAuth client secret |
| `MANHEIM_BASE_URL` | ❌ | `https://api.manheim.com` | Production API URL |
| `MANHEIM_SANDBOX_URL` | ❌ | `https://sandbox.manheim.com` | Testing API URL |
| `MANHEIM_TIMEOUT` | ❌ | `45000` | Request timeout (ms) |
| `MANHEIM_ENABLED` | ❌ | `false` | Enable Manheim integration |

**Partnership Requirements:**
- Manheim Data License Agreement
- SOC 2 Type II compliance
- Minimum transaction volume commitments

### Carfax Vehicle History

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CARFAX_API_KEY` | ❌ | `None` | Carfax API key |
| `CARFAX_CLIENT_ID` | ❌ | `None` | OAuth client ID |
| `CARFAX_CLIENT_SECRET` | ❌ | `None` | OAuth client secret |
| `CARFAX_CERT_PATH` | ❌ | `None` | Path to Carfax certificate |
| `CARFAX_BASE_URL` | ❌ | `https://api.carfax.com` | Carfax API base URL |
| `CARFAX_TIMEOUT` | ❌ | `60000` | Request timeout (ms) |
| `CARFAX_ENABLED` | ❌ | `false` | Enable Carfax integration |

**Partnership Requirements:**
- Carfax Data Provider Agreement
- $2M E&O and Cyber Liability insurance
- PCI DSS Level 1 compliance
- Annual security audits

## Payment Processing (Stripe)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STRIPE_SECRET_KEY` | ❌ | `None` | Stripe secret key (sk_live_* or sk_test_*) |
| `STRIPE_PUBLISHABLE_KEY` | ❌ | `None` | Stripe publishable key (pk_live_* or pk_test_*) |
| `STRIPE_WEBHOOK_SECRET` | ❌ | `None` | Webhook endpoint secret (whsec_*) |
| `STRIPE_WEBHOOK_ENDPOINT` | ❌ | `/api/webhooks/stripe` | Webhook endpoint path |

**Example:**
```bash
# Test keys for development
STRIPE_SECRET_KEY=sk_test_your_test_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Live keys for production
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key
```

## Rate Limiting

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_RATE_LIMIT_PER_MINUTE` | ❌ | `100` | Requests per minute per user |
| `API_BURST_LIMIT` | ❌ | `200` | Burst request limit |
| `RATE_LIMIT_STORAGE` | ❌ | `upstash` | Storage backend (`upstash`, `redis`, `memory`) |

**Example:**
```bash
API_RATE_LIMIT_PER_MINUTE=100
API_BURST_LIMIT=200
```

## Feature Flags

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEATURE_FLAGS` | ❌ | `packages_engine,valuations,history` | Comma-separated feature list |

**Available Features:**
- `packages_engine` - Enhanced VIN decoding
- `valuations` - Vehicle value estimates  
- `history` - Vehicle history reports
- `premium_features` - Premium subscription features
- `ai_insights` - AI-powered vehicle insights
- `batch_processing` - Bulk VIN processing

**Example:**
```bash
# Enable all features
FEATURE_FLAGS=packages_engine,valuations,history,premium_features

# Development - basic features only
FEATURE_FLAGS=packages_engine
```

## CORS Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CORS_ORIGINS` | ❌ | `http://localhost:3000,http://localhost:8000` | Allowed origins (comma-separated) |
| `CORS_ALLOW_CREDENTIALS` | ❌ | `true` | Allow credentials in CORS requests |
| `CORS_ALLOW_METHODS` | ❌ | `GET,POST,PUT,DELETE,OPTIONS` | Allowed HTTP methods |
| `CORS_ALLOW_HEADERS` | ❌ | `Content-Type,Authorization,X-API-Key` | Allowed headers |

**Example:**
```bash
# Development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Production
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

## Monitoring & Observability

### Sentry (Error Tracking)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTRY_DSN` | ❌ | `None` | Sentry Data Source Name |
| `SENTRY_ENVIRONMENT` | ❌ | `development` | Environment name |
| `SENTRY_TRACES_SAMPLE_RATE` | ❌ | `0.1` | Trace sampling rate (0.0-1.0) |
| `SENTRY_PROFILES_SAMPLE_RATE` | ❌ | `0.1` | Profile sampling rate (0.0-1.0) |

**Example:**
```bash
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### OpenTelemetry (Distributed Tracing)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | ❌ | `None` | OTLP endpoint URL |
| `OTEL_EXPORTER_OTLP_HEADERS` | ❌ | `None` | OTLP headers (e.g., API keys) |
| `OTEL_SERVICE_NAME` | ❌ | `vin-decoder-bot` | Service name |
| `OTEL_SERVICE_VERSION` | ❌ | `1.0.0` | Service version |
| `OTEL_RESOURCE_ATTRIBUTES` | ❌ | `deployment.environment=development` | Resource attributes |

**Example (Honeycomb):**
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.honeycomb.io
OTEL_EXPORTER_OTLP_HEADERS=x-honeycomb-team=your_api_key
OTEL_SERVICE_NAME=vin-decoder-bot
OTEL_SERVICE_VERSION=1.2.0
OTEL_RESOURCE_ATTRIBUTES=deployment.environment=production
```

## Application Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | ❌ | `development` | Environment name (`development`, `staging`, `production`) |
| `DEBUG` | ❌ | `false` | Enable debug mode |
| `LOG_LEVEL` | ❌ | `INFO` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `HTTP_TIMEOUT_SECONDS` | ❌ | `15` | Default HTTP timeout |

**Example:**
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
HTTP_TIMEOUT_SECONDS=30
```

## Environment-Specific Examples

### Development Environment

```bash
# .env for local development
TELEGRAM_BOT_TOKEN=your_bot_token_here
AUTODEV_API_KEY=your_autodev_key
DATABASE_URL=postgresql://postgres:secret@localhost:5432/vinbot
UPSTASH_REDIS_REST_URL=https://dev-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=dev_token
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
FEATURE_FLAGS=packages_engine
```

### Staging Environment

```bash
# Staging configuration
TELEGRAM_BOT_TOKEN=staging_bot_token
AUTODEV_API_KEY=staging_autodev_key
DATABASE_URL=postgresql://user:pass@staging-db:5432/vinbot
UPSTASH_REDIS_REST_URL=https://staging-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=staging_token
SENTRY_DSN=https://staging-dsn@sentry.io/project
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
FEATURE_FLAGS=packages_engine,valuations
```

### Production Environment

```bash
# Production configuration
TELEGRAM_BOT_TOKEN=prod_bot_token
AUTODEV_API_KEY=prod_autodev_key
MANHEIM_MMR_API_KEY=prod_manheim_key
CARFAX_API_KEY=prod_carfax_key
STRIPE_SECRET_KEY=sk_live_production_key
DATABASE_URL=postgresql://prod:secure@prod-db:5432/vinbot
UPSTASH_REDIS_REST_URL=https://prod-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=prod_token
SENTRY_DSN=https://prod-dsn@sentry.io/project
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
API_RATE_LIMIT_PER_MINUTE=1000
FEATURE_FLAGS=packages_engine,valuations,history,premium_features
CORS_ORIGINS=https://yourdomain.com
```

## Security Best Practices

### 1. Environment Variables
- Never commit `.env` files to version control
- Use different keys for each environment
- Rotate API keys regularly (monthly for production)
- Use secrets management for production (Vault, AWS Secrets Manager)

### 2. API Keys
- Store sensitive keys as `SecretStr` in Pydantic models
- Use least-privilege access for API keys
- Monitor API key usage and set up alerts

### 3. Database Security
- Use strong passwords and connection encryption
- Limit database user permissions
- Enable connection pooling and timeouts
- Regular security updates

### 4. Monitoring
- Enable Sentry for error tracking
- Set up OpenTelemetry for performance monitoring
- Monitor API usage and costs
- Set up alerting for critical errors

## Troubleshooting

### Common Issues

#### 1. Database Connection Failures
```bash
# Check database URL format
DATABASE_URL=postgresql://user:password@host:port/database

# Test connection
python -c "from src.config.dependencies import Container; print('DB OK' if Container().database_engine() else 'No DB')"
```

#### 2. Cache Connection Issues
```bash
# Verify Upstash credentials
# Check network connectivity to Upstash
curl -H "Authorization: Bearer $UPSTASH_REDIS_REST_TOKEN" $UPSTASH_REDIS_REST_URL/ping
```

#### 3. API Service Failures
```bash
# Test API connectivity
curl -H "X-API-Key: $AUTODEV_API_KEY" https://api.auto.dev/health
```

#### 4. Feature Flag Issues
```bash
# Validate feature flags format (comma-separated, no spaces)
FEATURE_FLAGS=packages_engine,valuations,history
```

### Logging and Debugging

Enable debug logging to troubleshoot configuration issues:

```bash
DEBUG=true
LOG_LEVEL=DEBUG
DB_ECHO_SQL=true
```

Check logs for configuration loading:
```bash
# Application startup logs show loaded configuration
grep "Settings loaded" /var/log/application.log
```

## Migration Guide

When updating configuration:

1. **Backup current `.env`**
2. **Update `.env.example`** with new variables
3. **Update documentation** in this file
4. **Test in development** before production
5. **Deploy gradually** (staging → production)

### Breaking Changes

#### v2.0.0 - Upstash Variable Naming
- Kept existing `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` 
- These are consistent with Upstash documentation
- No migration needed for existing deployments

#### v2.1.0 - New Service Integrations
- Added Manheim and Carfax variables (optional)
- Added Stripe payment processing (optional)
- Added comprehensive monitoring variables (optional)

---

**Last Updated:** January 2025  
**Next Review:** April 2025

For questions or issues with configuration, please check the troubleshooting section above or create an issue in the repository.
