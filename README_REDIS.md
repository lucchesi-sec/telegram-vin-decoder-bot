# Redis Caching Setup for VIN Bot on Fly.io

## Overview
Redis caching has been implemented to cache VIN lookup responses from the CarsXE API, reducing API calls and improving response times for duplicate VIN queries.

## Features
- **Automatic caching**: VIN lookups are automatically cached for 24 hours (configurable)
- **Cache hit/miss logging**: Track cache performance in logs
- **Graceful fallback**: If Redis is unavailable, the bot continues to work without caching
- **Configurable TTL**: Set cache expiration time via environment variable

## Setup Instructions

### 1. Create Redis Instance on Fly.io

Run the provided setup script:
```bash
chmod +x fly-setup-redis.sh
./fly-setup-redis.sh
```

Or manually:
```bash
# Create Redis instance
fly redis create --name vinbot-redis --region ewr --plan Free

# Attach Redis to your app (this sets REDIS_URL automatically)
fly redis attach vinbot-redis --app vinbot-decoder
```

### 2. Verify Redis Connection

Check that the Redis URL is set:
```bash
fly secrets list --app vinbot-decoder
```

You should see `REDIS_URL` in the list.

### 3. Deploy the Updated Bot

```bash
fly deploy --app vinbot-decoder
```

## Configuration

### Environment Variables

- `REDIS_URL`: Redis connection URL (automatically set by Fly.io when attaching Redis)
- `REDIS_TTL_SECONDS`: Cache time-to-live in seconds (default: 86400 = 24 hours)

### Example Configuration

```bash
# Set custom TTL (12 hours)
fly secrets set REDIS_TTL_SECONDS=43200 --app vinbot-decoder
```

## Monitoring

### View Cache Performance

Check application logs to see cache hits and misses:
```bash
fly logs --app vinbot-decoder | grep -E "Cache (hit|miss)"
```

### Redis Statistics

Connect to Redis to view statistics:
```bash
fly redis connect vinbot-redis
> INFO stats
> DBSIZE
> KEYS vin:*
```

## Cache Key Format

VIN data is cached with keys in the format:
```
vin:{VIN_UPPERCASE}
```

Example: `vin:1HGBH41JXMN109186`

## Implementation Details

### Files Modified
- `requirements.txt`: Added `redis~=5.0.0`
- `vinbot/redis_cache.py`: New Redis cache implementation
- `vinbot/carsxe_client.py`: Integrated cache checking and storing
- `vinbot/config.py`: Added Redis configuration parameters
- `vinbot/bot.py`: Initialize Redis cache on startup

### Cache Flow
1. User requests VIN decode
2. Bot checks Redis cache for existing data
3. If cache hit: Return cached data immediately
4. If cache miss: Query CarsXE API, cache response, return data
5. Cached data expires after TTL seconds

## Troubleshooting

### Redis Connection Issues
If Redis connection fails, check:
1. Redis instance status: `fly redis list`
2. App secrets: `fly secrets list --app vinbot-decoder`
3. Application logs: `fly logs --app vinbot-decoder`

### Cache Not Working
1. Verify REDIS_URL is set correctly
2. Check Redis instance is running: `fly redis status vinbot-redis`
3. Review application logs for Redis connection errors

## Cost Considerations

The Free tier Redis on Fly.io includes:
- 100MB RAM
- Single node (no replication)
- Suitable for caching thousands of VIN lookups

For production use, consider upgrading to a paid plan for:
- Higher memory capacity
- Replication for high availability
- Automatic backups