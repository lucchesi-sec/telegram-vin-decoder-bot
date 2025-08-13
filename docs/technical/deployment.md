# IntelAuto Platform Deployment Notes

## Overview

IntelAuto is deployed as a multi-service platform with two independent but integrated services:

1. **Web Platform Service**: Professional interface with FastAPI backend + Next.js frontend
2. **Telegram Bot Service**: Conversational AI for instant vehicle intelligence

Both services share infrastructure (PostgreSQL database, Redis cache) while maintaining independent scaling and health monitoring.

## Current Deployment Configuration

### Platform Architecture
```
┌─────────────────────────────────────┐
│         Fly.io Platform             │
├─────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────┐ │
│  │  Telegram    │  │     Web     │ │
│  │  Bot Service │  │  Platform   │ │
│  │   (Port      │  │  Service    │ │
│  │   8080)      │  │  (Port      │ │
│  │              │  │   8000)     │ │
│  └──────────────┘  └─────────────┘ │
│         │                  │        │
│         └──────┬───────────┘        │
│                │                    │
│     ┌──────────▼──────────┐         │
│     │   PostgreSQL DB     │         │
│     └─────────────────────┘         │
└─────────────────────────────────────┘
                 │
     ┌───────────▼───────────┐
     │   Upstash Redis       │
     │   (External Cache)    │
     └───────────────────────┘
```

### Service Definitions

#### Web Platform Service
- **External Traffic**: HTTPS on port 443 → internal port 8000
- **Internal Components**: 
  - Next.js frontend (port 8000) - public interface
  - FastAPI backend (port 5000) - internal API
- **Health Check**: Next.js `/health` endpoint
- **Process**: `web` → `./web-entrypoint.sh`
- **Users**: Business professionals, API clients, web dashboard users

#### Telegram Bot Service  
- **Internal Service**: TCP health checks on port 8080
- **Function**: Webhook processing, conversational AI
- **Health Check**: Internal HTTP server with `/health` and `/ready` endpoints
- **Process**: `bot` → `./entrypoint.sh`
- **Users**: Telegram users, mobile professionals

## Health Check Endpoints

### Web Platform Health Checks

1. **Next.js Frontend** (Public):
   ```bash
   curl https://vinbot-decoder-v2.fly.dev/health
   # Expected: 200 OK "ok"
   ```

2. **FastAPI Backend** (Internal):
   ```bash
   curl http://localhost:5000/health
   # Expected: {
   #   "status": "healthy",
   #   "timestamp": "2025-01-12T15:30:00Z",
   #   "database": "healthy",
   #   "cache": "healthy"
   # }
   ```

### Telegram Bot Health Checks

1. **Internal Health Server** (Port 8080):
   ```bash
   curl http://localhost:8080/health
   # Expected: {
   #   "status": "healthy",
   #   "timestamp": 1642000000,
   #   "service": "vinbot-decoder"
   # }
   ```

2. **Readiness Check**:
   ```bash
   curl http://localhost:8080/ready
   # Expected: {
   #   "status": "ready",
   #   "dependencies": {
   #     "telegram_api": "unknown",
   #     "external_services": "unknown"
   #   }
   # }
   ```

## Deployment Options

### Option 1: Multi-Process Production Deployment (Current)

**Best For**: Production environments, independent scaling

```yaml
Configuration: fly.toml
Processes: 2 independent VMs
Scaling: Independent per service
Health: Service-specific monitoring
Cost: ~$10/month
```

**Deployment**:
```bash
fly deploy
fly scale count web=2    # Scale web service
fly scale count bot=1    # Keep bot service minimal
```

### Option 2: Single-Process Development Deployment

**Best For**: Development, testing, cost optimization

```yaml
Configuration: Modified fly.toml
Processes: 1 combined VM (1GB RAM)
Scaling: Manual restart required
Health: Combined health checks
Cost: ~$5/month
```

**Setup**: Create `combined-entrypoint.sh`:
```bash
#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
python -m uvicorn src.presentation.api.domain_api_server:app --host 0.0.0.0 --port 5000 &

echo "Starting Telegram bot..."
python -m src.main &

echo "Starting web dashboard..."
cd src/presentation/web-dashboard-next
export PORT=8000
export HOSTNAME=0.0.0.0  
export BACKEND_URL=http://localhost:5000
npm run start &

wait
```

## Service Entry Points

### Web Platform Entry Point (`web-entrypoint.sh`)
1. Starts FastAPI backend on port 5000
2. Starts Next.js frontend on port 8000
3. Configures backend URL for API communication
4. Manages both processes with proper error handling

### Bot Service Entry Point (`entrypoint.sh`)
1. Runs database migrations with retry logic
2. Starts Telegram bot with webhook support
3. Initializes health check server on port 8080
4. Handles graceful shutdown

## Scaling Strategy

### Independent Scaling (Multi-Process)
```bash
# Scale web platform for increased traffic
fly scale count web=3

# Scale bot service for webhook processing
fly scale count bot=2

# Check scaling status
fly status
```

### Resource Allocation
- **Web Service VM**: 512MB RAM, shared CPU (handles HTTP traffic + API processing)
- **Bot Service VM**: 512MB RAM, shared CPU (handles webhooks + AI processing)

### Traffic Distribution
- **Web Traffic**: Load balanced across web service instances
- **Bot Traffic**: Telegram webhooks distributed across bot instances
- **Database**: Shared connection pool across all services

## Monitoring & Health

### Fly.io Health Checks
- **Web Service**: HTTP GET `/health` every 30s
- **Bot Service**: TCP health check on port 8080 every 30s
- **Grace Period**: 30s for service startup
- **Timeout**: 10s per health check

### Application-Level Monitoring
- **Sentry**: Error tracking across all services
- **Database Monitoring**: Connection pool health via health endpoints
- **Cache Monitoring**: Redis connection status via health endpoints

### Log Aggregation
```bash
# View all services
fly logs --app vinbot-decoder-v2

# View specific service
fly logs --app vinbot-decoder-v2 --type web
fly logs --app vinbot-decoder-v2 --type bot
```

## Environment Variables

### Required for Both Services
```bash
DATABASE_URL=postgresql://postgres:password@hostname:5432/database
UPSTASH_REDIS_REST_URL=https://your-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token
SENTRY_DSN=https://sentry-dsn@sentry.io/project
```

### Web Platform Specific
```bash
DASHBOARD_SECRET_KEY=your-secret-key
DASHBOARD_ALLOWED_ORIGINS=https://yourdomain.com
JWT_SECRET=your-jwt-secret
```

### Bot Service Specific  
```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_URL=https://your-app.fly.dev/webhook
```

### External Service APIs
```bash
AUTODEV_API_KEY=your-autodev-key
DEFAULT_DECODER_SERVICE=autodev
```

## SSL/TLS Configuration

### Automatic SSL
- Fly.io provides automatic SSL/TLS certificates
- Force HTTPS enabled in `fly.toml`
- Certificates auto-renewed

### Custom Domain Setup
```bash
# Add custom domain
fly certs add yourdomain.com

# Check certificate status
fly certs show yourdomain.com
```

## Database & Cache

### PostgreSQL Database
- **Shared**: Both services use same database
- **Connection Pooling**: Managed per service
- **Migrations**: Run by bot service during startup
- **Backup**: Managed by Fly.io Postgres

### Redis Cache (Upstash)
- **External Service**: Serverless Redis
- **Shared**: Both services use same cache
- **TTL**: 30 days for VIN data, 1 hour for general cache
- **Monitoring**: Health checks via API endpoints

## Security Considerations

### Network Security
- **Internal Communication**: Services communicate via localhost
- **External Access**: Only web service exposed to internet
- **CORS**: Configured for specific origins only

### Data Security
- **Environment Variables**: Stored as Fly.io secrets
- **API Keys**: Rotated regularly via dashboard
- **Database**: SSL connections enforced
- **Cache**: TLS encryption via Upstash

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   fly logs --app vinbot-decoder-v2
   # Check for dependency issues or configuration errors
   ```

2. **Health Check Failures**
   ```bash
   fly status
   # Verify health check endpoints are responding
   ```

3. **Database Connection Issues**
   ```bash
   fly postgres connect --app your-postgres-app
   # Verify database connectivity and credentials
   ```

### Emergency Procedures

1. **Rollback Deployment**
   ```bash
   fly releases
   fly deploy --image <previous-image-id>
   ```

2. **Scale Down for Issues**
   ```bash
   fly scale count web=1 bot=0  # Emergency: disable bot, minimize web
   ```

3. **Restart Services**
   ```bash
   fly restart web
   fly restart bot
   ```

## Performance Optimization

### Resource Tuning
- **Web Service**: Increase RAM for high traffic periods
- **Bot Service**: Monitor webhook processing delays
- **Database**: Connection pool optimization
- **Cache**: TTL tuning based on usage patterns

### Scaling Triggers
- **Web Service**: Scale up when response times > 2s
- **Bot Service**: Scale up when webhook queue > 100 messages
- **Database**: Monitor connection pool utilization
- **Cache**: Monitor hit/miss ratios

---

## Quick Reference Commands

### Deployment
```bash
fly deploy                                    # Deploy both services
fly scale count web=2 bot=1                  # Scale services
fly status                                   # Check service status
```

### Monitoring
```bash
fly logs --app vinbot-decoder-v2             # All logs
fly logs --app vinbot-decoder-v2 --type web  # Web service logs
fly logs --app vinbot-decoder-v2 --type bot  # Bot service logs
```

### Health Checks
```bash
curl https://vinbot-decoder-v2.fly.dev/health  # Public health check
fly ssh console --app vinbot-decoder-v2        # Internal access
```

### Secrets Management
```bash
fly secrets list                              # List secrets
fly secrets set KEY=value                     # Set secret
fly secrets unset KEY                         # Remove secret
```
