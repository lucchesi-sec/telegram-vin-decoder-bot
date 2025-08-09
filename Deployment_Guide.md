# VIN Bot Deployment Guide for Fly.io

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Initial Setup](#initial-setup)
4. [Configuration](#configuration)
5. [Deployment Process](#deployment-process)
6. [Redis Cache Setup](#redis-cache-setup)
7. [Monitoring & Logs](#monitoring--logs)
8. [Updating & Maintenance](#updating--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)
11. [Cost Management](#cost-management)
12. [Rollback Procedures](#rollback-procedures)

## Overview

This guide covers the complete deployment process for the VIN Bot Telegram application on Fly.io, including Redis caching integration for optimized API usage.

### Architecture Components
- **Telegram Bot**: Python application using python-telegram-bot
- **VIN API**: CarsXE API for VIN decoding
- **Redis Cache**: In-memory cache for API responses
- **Hosting**: Fly.io container platform
- **Region**: Primary deployment in `ewr` (US East)

## Prerequisites

### Required Accounts
1. **Fly.io Account**: Sign up at [fly.io](https://fly.io)
2. **Telegram Bot Token**: Obtain from [@BotFather](https://t.me/botfather)
3. **CarsXE API Key**: Register at [carsxe.com](https://www.carsxe.com)

### Local Development Tools
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Verify installation
fly version

# Install Python 3.8+
python3 --version

# Install Git
git --version
```

### API Credentials
Ensure you have:
- `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
- `CARSXE_API_KEY`: Your CarsXE API key

## Initial Setup

### 1. Authenticate with Fly.io
```bash
# Login to Fly.io
fly auth login

# Verify authentication
fly auth whoami
```

### 2. Create Fly Application
```bash
# Navigate to project directory
cd /path/to/Telegram_Bot

# Create new Fly app
fly apps create vinbot-decoder

# Verify app creation
fly apps list
```

### 3. Set Application Secrets
```bash
# Set required environment variables
fly secrets set TELEGRAM_BOT_TOKEN="your-telegram-bot-token" --app vinbot-decoder
fly secrets set CARSXE_API_KEY="your-carsxe-api-key" --app vinbot-decoder

# Optional: Set custom configurations
fly secrets set LOG_LEVEL="INFO" --app vinbot-decoder
fly secrets set HTTP_TIMEOUT_SECONDS="15" --app vinbot-decoder
```

## Configuration

### fly.toml Configuration
The `fly.toml` file defines your application configuration:

```toml
# fly.toml
app = 'vinbot-decoder'
primary_region = 'ewr'

[build]
  # Uses Dockerfile for building

[processes]
  app = "python -m vinbot"

[[vm]]
  memory = '1gb'
  cpu_kind = 'shared'
  cpus = 1
```

### Dockerfile Configuration
Ensure your Dockerfile is optimized:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY vinbot/ ./vinbot/

# Run the bot
CMD ["python", "-m", "vinbot"]
```

## Deployment Process

### 1. Initial Deployment
```bash
# Deploy the application
fly deploy --app vinbot-decoder

# Monitor deployment
fly status --app vinbot-decoder
```

### 2. Verify Deployment
```bash
# Check application status
fly apps list

# View running instances
fly scale show --app vinbot-decoder

# Check application logs
fly logs --app vinbot-decoder
```

### 3. Health Checks
```bash
# View app health
fly checks list --app vinbot-decoder

# Monitor real-time metrics
fly monitor --app vinbot-decoder
```

## Redis Cache Setup

### 1. Create Redis Instance
```bash
# Create Redis database
fly redis create \
  --name vinbot-redis \
  --region ewr \
  --plan Free

# Verify Redis creation
fly redis list
```

### 2. Connect Redis to Application
```bash
# Attach Redis to your app (automatically sets REDIS_URL)
fly redis attach vinbot-redis --app vinbot-decoder

# Verify connection
fly redis status vinbot-redis
```

### 3. Configure Cache Settings
```bash
# Optional: Set custom cache TTL (default: 24 hours)
fly secrets set REDIS_TTL_SECONDS="86400" --app vinbot-decoder

# List all secrets to verify
fly secrets list --app vinbot-decoder
```

### 4. Test Redis Connection
```bash
# Connect to Redis CLI
fly redis connect vinbot-redis

# In Redis CLI, test commands:
> PING
> INFO server
> DBSIZE
> exit
```

## Monitoring & Logs

### Application Logs
```bash
# View recent logs
fly logs --app vinbot-decoder

# Stream live logs
fly logs --app vinbot-decoder --tail

# Filter logs by level
fly logs --app vinbot-decoder | grep ERROR

# View cache performance
fly logs --app vinbot-decoder | grep -E "Cache (hit|miss)"
```

### Metrics & Monitoring
```bash
# View CPU and memory usage
fly status --app vinbot-decoder

# Monitor instance metrics
fly monitor --app vinbot-decoder

# Check Redis metrics
fly redis status vinbot-redis --json
```

### Setting Up Alerts
```bash
# Configure log alerts (via Fly dashboard)
# 1. Go to https://fly.io/apps/vinbot-decoder/monitoring
# 2. Set up alerts for:
#    - High error rates
#    - Memory usage > 80%
#    - Instance restarts
```

## Updating & Maintenance

### Deploying Updates
```bash
# 1. Make code changes locally
# 2. Test changes
python -m vinbot  # Local testing

# 3. Deploy updates
fly deploy --app vinbot-decoder

# 4. Monitor deployment
fly logs --app vinbot-decoder --tail
```

### Rolling Updates
```bash
# Deploy with strategy
fly deploy --app vinbot-decoder --strategy rolling

# Check deployment status
fly status --app vinbot-decoder --watch
```

### Database Maintenance
```bash
# Clear Redis cache if needed
fly redis connect vinbot-redis
> FLUSHDB
> exit

# Monitor Redis memory usage
fly redis status vinbot-redis
```

## Troubleshooting

### Common Issues and Solutions

#### Bot Not Responding
```bash
# Check if app is running
fly status --app vinbot-decoder

# View error logs
fly logs --app vinbot-decoder | grep ERROR

# Restart application
fly apps restart vinbot-decoder
```

#### Redis Connection Issues
```bash
# Check Redis status
fly redis status vinbot-redis

# Verify REDIS_URL is set
fly secrets list --app vinbot-decoder

# Test Redis connectivity
fly redis connect vinbot-redis
> PING
```

#### High Memory Usage
```bash
# Check current usage
fly status --app vinbot-decoder

# Scale up if needed
fly scale memory 2048 --app vinbot-decoder

# Or optimize cache TTL
fly secrets set REDIS_TTL_SECONDS="43200" --app vinbot-decoder
```

#### API Rate Limiting
```bash
# Check for rate limit errors
fly logs --app vinbot-decoder | grep "rate limit"

# Increase cache TTL to reduce API calls
fly secrets set REDIS_TTL_SECONDS="172800" --app vinbot-decoder
```

### Debug Mode
```bash
# Enable debug logging
fly secrets set LOG_LEVEL="DEBUG" --app vinbot-decoder

# Deploy with debug mode
fly deploy --app vinbot-decoder

# View debug logs
fly logs --app vinbot-decoder | grep DEBUG
```

## Security Best Practices

### 1. Secrets Management
```bash
# Never commit secrets to git
# Use fly secrets for all sensitive data
fly secrets list --app vinbot-decoder

# Rotate API keys periodically
fly secrets set TELEGRAM_BOT_TOKEN="new-token" --app vinbot-decoder
fly secrets set CARSXE_API_KEY="new-key" --app vinbot-decoder
```

### 2. Network Security
```bash
# Redis is only accessible internally
# No public ports exposed except what's needed

# Verify no unnecessary ports
fly info --app vinbot-decoder
```

### 3. Access Control
```bash
# Limit team access
fly orgs members list

# Use deploy tokens for CI/CD
fly tokens create deploy
```

### 4. Regular Updates
```bash
# Keep dependencies updated
pip list --outdated
pip install --upgrade -r requirements.txt

# Update base Docker image
# Edit Dockerfile to use latest Python version
```

## Cost Management

### Free Tier Limits
- **Fly.io Free Tier**:
  - 3 shared-cpu-1x VMs with 256MB RAM
  - 3GB persistent storage
  - 160GB outbound transfer

- **Redis Free Tier**:
  - 100MB RAM
  - Single node
  - No backups

### Monitoring Usage
```bash
# Check current usage
fly dashboard metrics

# Monitor Redis memory
fly redis status vinbot-redis

# View billing
fly billing dashboard
```

### Optimization Tips
1. **Cache Aggressively**: Increase `REDIS_TTL_SECONDS` to reduce API calls
2. **Right-size Resources**: Start small, scale as needed
3. **Regional Deployment**: Deploy close to users to reduce latency
4. **Monitor Metrics**: Regular monitoring prevents surprise charges

## Rollback Procedures

### Application Rollback
```bash
# List recent deployments
fly releases --app vinbot-decoder

# Rollback to previous version
fly deploy --app vinbot-decoder --image registry.fly.io/vinbot-decoder:v[VERSION]

# Or use release ID
fly releases rollback [RELEASE_ID] --app vinbot-decoder
```

### Configuration Rollback
```bash
# View secret history (via dashboard)
# https://fly.io/apps/vinbot-decoder/secrets

# Manually reset secrets
fly secrets set TELEGRAM_BOT_TOKEN="old-token" --app vinbot-decoder
```

### Emergency Procedures
```bash
# Stop application immediately
fly scale count 0 --app vinbot-decoder

# Restart after fixing issues
fly scale count 1 --app vinbot-decoder

# Full restart
fly apps restart vinbot-decoder
```

## Deployment Checklist

### Pre-Deployment
- [ ] Test locally with production-like data
- [ ] Verify all API keys are valid
- [ ] Check Dockerfile builds successfully
- [ ] Review fly.toml configuration
- [ ] Ensure requirements.txt is up to date

### Deployment
- [ ] Run `fly deploy --app vinbot-decoder`
- [ ] Monitor deployment logs
- [ ] Verify application starts successfully
- [ ] Check health checks pass
- [ ] Test bot functionality

### Post-Deployment
- [ ] Send test VIN to bot
- [ ] Verify Redis caching works
- [ ] Check error logs
- [ ] Monitor memory/CPU usage
- [ ] Set up monitoring alerts

## Support Resources

### Documentation
- [Fly.io Documentation](https://fly.io/docs)
- [Python Telegram Bot Docs](https://python-telegram-bot.readthedocs.io)
- [Redis Documentation](https://redis.io/documentation)

### Community Support
- [Fly.io Community Forum](https://community.fly.io)
- [Telegram Bot API Support](https://t.me/BotSupport)

### Monitoring Dashboard
- Application: https://fly.io/apps/vinbot-decoder
- Metrics: https://fly.io/apps/vinbot-decoder/monitoring
- Logs: https://fly.io/apps/vinbot-decoder/logs

## Quick Commands Reference

```bash
# Deployment
fly deploy --app vinbot-decoder

# Status
fly status --app vinbot-decoder
fly logs --app vinbot-decoder

# Secrets
fly secrets list --app vinbot-decoder
fly secrets set KEY="value" --app vinbot-decoder

# Redis
fly redis status vinbot-redis
fly redis connect vinbot-redis

# Scaling
fly scale show --app vinbot-decoder
fly scale memory 2048 --app vinbot-decoder

# Restart
fly apps restart vinbot-decoder
```

---

*Last Updated: 2025*
*Version: 1.0.0*