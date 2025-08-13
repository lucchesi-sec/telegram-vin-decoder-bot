# Infrastructure Deployment Guide

## IntelAuto Platform Architecture

### Multi-Service Platform Overview
IntelAuto is a comprehensive vehicle intelligence platform consisting of two independent but integrated services:

- **Web Platform Service**: FastAPI backend + Next.js frontend for professional vehicle analytics
- **Telegram Bot Service**: Conversational AI service for instant vehicle intelligence
- **Shared Infrastructure**: PostgreSQL database, Upstash Redis cache, Sentry monitoring

Both services operate independently with separate scaling, health checks, and deployment processes while sharing core business logic and data.

## Recommended Infrastructure Stack

### 🏆 **Option 1: Fly.io Unified Deployment (RECOMMENDED)**

#### Why This Approach?
- Single deployment platform
- Shared PostgreSQL database
- Automatic SSL/TLS
- Built-in health checks
- Cost-effective (~$5-10/month)

#### Architecture:
```
┌─────────────────────────────────────┐
│         Fly.io Platform             │
├─────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────┐ │
│  │  Telegram    │  │     Web     │ │
│  │     Bot      │  │  Dashboard  │ │
│  │  Process     │  │   Process   │ │
│  └──────┬───────┘  └──────┬──────┘ │
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

#### Implementation Steps:
1. Update `fly.toml` to use multi-process configuration
2. Deploy with: `fly deploy --config fly.toml.new`
3. Set up custom domain: `fly certs add yourdomain.com`

---

### 🌐 **Option 2: Hybrid Deployment (Vercel + Fly.io)**

#### Why This Approach?
- Static frontend on CDN (faster)
- Separate scaling for frontend/backend
- Free tier on Vercel
- API remains on Fly.io

#### Architecture:
```
┌──────────────────┐     ┌──────────────────┐
│   Vercel CDN     │────▶│    Fly.io        │
│   (Frontend)     │     │   (Backend)      │
│                  │     │                  │
│  - HTML/CSS/JS   │     │  - Telegram Bot  │
│  - Static Assets │     │  - API Endpoints │
└──────────────────┘     └─────────┬────────┘
                                    │
                         ┌──────────▼────────┐
                         │   PostgreSQL DB   │
                         └───────────────────┘
```

#### Implementation:
```bash
# Deploy frontend to Vercel
vercel --prod

# Keep backend on Fly.io
fly deploy
```

---

### 🚀 **Option 3: Container Orchestration (Railway/Render)**

#### Why This Approach?
- Simple GitHub integration
- Automatic deployments
- Built-in database provisioning
- Good for teams

#### Architecture:
```
┌─────────────────────────────────────┐
│      Railway/Render Platform        │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐  │
│  │    Docker Container           │  │
│  │  ┌──────────┐  ┌───────────┐ │  │
│  │  │   Bot    │  │ Dashboard │ │  │
│  │  └──────────┘  └───────────┘ │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   Managed PostgreSQL          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## Migration Path from Current Setup

### Step 1: Database Configuration
```bash
# Ensure DATABASE_URL supports multiple connections
fly postgres attach --app vinbot-decoder-v2
```

### Step 2: Environment Variables
```bash
# Add dashboard-specific configs
fly secrets set \
  DASHBOARD_SECRET_KEY="$(openssl rand -hex 32)" \
  DASHBOARD_ALLOWED_ORIGINS="https://yourdomain.com" \
  --app vinbot-decoder-v2
```

### Step 3: Update Dockerfile
```dockerfile
# Use Dockerfile.multi for both services
FROM python:3.11-slim
# ... (see Dockerfile.multi)
```

### Step 4: Deploy
```bash
# Deploy with new configuration
fly deploy --config fly.toml.new
```

---

## Cost Analysis

### Fly.io (Recommended)
- **Shared VM**: $5/month (both services)
- **PostgreSQL**: $0 (shared with bot)
- **Bandwidth**: ~$0.02/GB
- **Total**: ~$5-10/month

### Vercel + Fly.io
- **Vercel**: Free (hobby tier)
- **Fly.io**: $5/month (bot only)
- **Total**: ~$5/month

### Railway/Render
- **Starter**: $5/month
- **Database**: $7/month
- **Total**: ~$12/month

---

## Security Considerations

1. **API Authentication**
   - Add API key authentication for dashboard endpoints
   - Use JWT tokens for user sessions

2. **CORS Configuration**
   - Restrict origins to your domain only
   - Update FastAPI CORS middleware

3. **Rate Limiting**
   - Implement rate limiting on decode endpoint
   - Use Redis for distributed rate limiting

4. **Database Security**
   - Use connection pooling
   - Implement row-level security if needed

---

## Monitoring Setup

### Add Dashboard Metrics
```python
# Add to dashboard app
from prometheus_client import Counter, Histogram

decode_counter = Counter('vin_decodes_total', 'Total VIN decodes')
response_time = Histogram('http_response_time_seconds', 'Response time')
```

### Sentry Integration
```python
# Already configured in main app
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()]
)
```

---

## Quick Start Commands

### Deploy to Fly.io (Recommended)
```bash
# 1. Update fly.toml
mv fly.toml.new fly.toml

# 2. Deploy
fly deploy

# 3. Open dashboard
fly open
```

### Deploy to Vercel (Frontend only)
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
vercel --prod

# 3. Set environment variable
vercel env add API_BASE_URL
```

---

## DNS Configuration

### For Custom Domain
```
# A Records
@ -> fly.io IP
www -> fly.io IP

# Or CNAME
www -> vinbot-decoder-v2.fly.dev
```

### SSL Certificate
```bash
fly certs add yourdomain.com
```

---

## Deployment Configurations

### Multi-Process Deployment (Recommended)

**Use Case**: Production environments requiring both web platform and Telegram bot services

**Configuration**: Current `fly.toml` setup with separate VMs for each process

```bash
# Deploy both services with independent scaling
fly deploy

# Scale web service for higher traffic
fly scale count web=2

# Scale bot service for webhook processing
fly scale count bot=1

# Monitor both services
fly status
fly logs --app vinbot-decoder-v2
```

**Benefits**:
- Independent scaling per service
- Isolated resource allocation
- Service-specific health monitoring
- Better fault tolerance

**Monitoring**:
- Web service health: `https://your-app.fly.dev/health`
- Bot service health: Internal TCP health checks on port 8080
- FastAPI backend: Internal health checks at `/health` endpoint

### Single-Process Deployment

**Use Case**: Development, testing, or cost-optimized deployments

**Setup**: Modify `fly.toml` to run both services on one machine

```toml
# Single-process configuration (development only)
[processes]
  app = './combined-entrypoint.sh'  # Custom script running both services

# Single VM configuration
[[vm]]
  memory = '1gb'  # Increased memory for both services
  cpu_kind = 'shared'
  cpus = 1
  processes = ['app']

[http_service]
  internal_port = 8000
  processes = ['app']  # Same process handles web traffic
```

**Create combined entrypoint**:
```bash
# Create combined-entrypoint.sh
#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
python -m uvicorn src.presentation.api.domain_api_server:app --host 0.0.0.0 --port 5000 &
API_PID=$!

echo "Starting Telegram bot..."
python -m src.main &
BOT_PID=$!

echo "Starting web dashboard..."
cd src/presentation/web-dashboard-next
export PORT=8000
export HOSTNAME=0.0.0.0
export BACKEND_URL=http://localhost:5000
npm run start &
WEB_PID=$!

wait $API_PID $BOT_PID $WEB_PID
```

**Deployment**:
```bash
# Make script executable
chmod +x combined-entrypoint.sh

# Deploy single-process version
fly deploy

# Monitor all services in one machine
fly logs
```

**Trade-offs**:
- ✅ Lower cost (single VM)
- ✅ Simpler deployment
- ❌ No independent scaling
- ❌ Single point of failure
- ❌ Resource contention between services

### Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| **Process Model** | Single-process | Multi-process |
| **VM Configuration** | 1 VM, 1GB RAM | 2 VMs, 512MB each |
| **Health Checks** | Combined | Service-specific |
| **Scaling** | Manual restart | Independent scaling |
| **Cost** | ~$5/month | ~$10/month |
| **Monitoring** | Basic logs | Service-specific metrics |

### Health Check Strategy

#### Multi-Process Health Checks
- **Web Service**: Next.js `/health` endpoint (port 8000)
- **Bot Service**: Internal TCP health on port 8080
- **FastAPI Backend**: Internal `/health` endpoint (port 5000)

#### Single-Process Health Checks
- **Combined Service**: Single HTTP health check covers all components
- **Fallback**: If Next.js fails, FastAPI health endpoint still available

```bash
# Check health in multi-process deployment
curl https://your-app.fly.dev/health  # Next.js frontend
curl http://localhost:5000/health     # FastAPI backend (internal)

# Check health in single-process deployment
curl https://your-app.fly.dev/health  # Combined health status
```

### Switching Between Deployments

#### From Single to Multi-Process
```bash
# 1. Backup current configuration
cp fly.toml fly.toml.single

# 2. Restore multi-process configuration
git checkout main -- fly.toml

# 3. Deploy with multi-process setup
fly deploy

# 4. Verify both services are running
fly status
```

#### From Multi to Single-Process
```bash
# 1. Create single-process fly.toml
# (see configuration above)

# 2. Create combined entrypoint script
# (see script above)

# 3. Deploy single-process version
fly deploy

# 4. Verify combined service is running
fly status
```

---

## Health Check Endpoint Documentation

### Web Platform Health Checks

**Next.js Frontend Health** (`/health`):
```bash
curl https://your-app.fly.dev/health
# Response: 200 OK "ok"
```

**FastAPI Backend Health** (`/health`):
```bash
curl http://localhost:5000/health
# Response: {
#   "status": "healthy",
#   "timestamp": "2025-01-12T15:30:00Z",
#   "database": "healthy",
#   "cache": "healthy"
# }
```

### Telegram Bot Health Checks

**Internal TCP Health** (Port 8080):
- Monitored by Fly.io TCP health checks
- Custom HTTP health server in `src/infrastructure/monitoring/http_health.py`
- Endpoints: `/health` (basic), `/ready` (dependencies)

```bash
# Internal health check (from within the bot process)
curl http://localhost:8080/health
# Response: {
#   "status": "healthy",
#   "timestamp": 1642000000,
#   "service": "vinbot-decoder"
# }
```

---

## Rollback Strategy

If issues arise:
```bash
# Rollback to previous version
fly releases
fly deploy --image <previous-image-id>

# Or restore original configuration
git checkout main -- fly.toml
fly deploy
```