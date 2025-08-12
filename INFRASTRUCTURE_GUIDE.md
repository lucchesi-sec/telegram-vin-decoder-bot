# Infrastructure Deployment Guide

## Current Architecture
- **Telegram Bot**: Python application running on Fly.io
- **Database**: PostgreSQL (likely Supabase or Fly Postgres)
- **Cache**: Upstash Redis
- **Monitoring**: Sentry
- **NEW**: Web Dashboard (FastAPI + Static Frontend)

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