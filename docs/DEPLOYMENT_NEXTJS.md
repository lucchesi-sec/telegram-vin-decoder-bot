# Next.js Dashboard Deployment Guide

## Overview
This guide covers deploying the Next.js-based VIN Decoder Dashboard to various platforms.

## Prerequisites
- Node.js 20+ and npm
- Git
- Backend API running (FastAPI)

## Deployment Options

### 1. Vercel (Recommended for Next.js)

Vercel is the company behind Next.js and provides the best deployment experience.

#### Steps:
1. Push your code to GitHub/GitLab/Bitbucket
2. Import project on [Vercel](https://vercel.com)
3. Configure build settings:
   ```
   Framework Preset: Next.js
   Root Directory: src/presentation/web-dashboard-next
   Build Command: npm run build
   Output Directory: .next
   ```
4. Add environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-domain.com
   ```
5. Deploy

#### Vercel CLI Deployment:
```bash
cd src/presentation/web-dashboard-next
npm i -g vercel
vercel

# Follow prompts to configure project
# Set environment variables in Vercel dashboard
```

### 2. Docker Deployment

#### Multi-stage Dockerfile:
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app

# Install production dependencies
COPY package*.json ./
RUN npm ci --production

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.ts ./

EXPOSE 3000
ENV NODE_ENV=production
CMD ["npm", "start"]
```

#### Docker Compose (Full Stack):
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: vindb
      POSTGRES_USER: vinuser
      POSTGRES_PASSWORD: vinpass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: 
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://vinuser:vinpass@postgres:5432/vindb
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
    depends_on:
      - postgres

  dashboard:
    build:
      context: ./src/presentation/web-dashboard-next
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://api:5000
    depends_on:
      - api

volumes:
  postgres_data:
```

### 3. Self-Hosted with PM2

#### Installation:
```bash
npm install -g pm2
```

#### Build and Deploy:
```bash
cd src/presentation/web-dashboard-next
npm run build

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'vin-dashboard',
    script: 'npm',
    args: 'start',
    env: {
      NODE_ENV: 'production',
      PORT: 3000,
      NEXT_PUBLIC_API_URL: 'https://api.yourdomain.com'
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 4. Nginx Reverse Proxy Setup

#### Nginx Configuration:
```nginx
server {
    listen 80;
    server_name dashboard.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dashboard.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. AWS Deployment

#### Using AWS Amplify:
1. Connect your GitHub repository
2. Configure build settings:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd src/presentation/web-dashboard-next
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: src/presentation/web-dashboard-next/.next
       files:
         - '**/*'
     cache:
       paths:
         - src/presentation/web-dashboard-next/node_modules/**/*
   ```

#### Using EC2 with Node.js:
```bash
# On EC2 instance
sudo yum update -y
curl -sL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install nodejs -y

# Clone repository
git clone https://github.com/yourusername/vin-decoder.git
cd vin-decoder/src/presentation/web-dashboard-next

# Install dependencies and build
npm ci
npm run build

# Install PM2 and start
sudo npm install -g pm2
pm2 start npm --name "dashboard" -- start
```

### 6. Railway Deployment

1. Connect GitHub repository
2. Add environment variables
3. Configure build settings:
   ```
   Build Command: cd src/presentation/web-dashboard-next && npm run build
   Start Command: cd src/presentation/web-dashboard-next && npm start
   ```

## Environment Variables

### Required:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Optional:
```env
# Port configuration
PORT=3000

# Analytics (if configured)
NEXT_PUBLIC_GA_ID=UA-XXXXXXXXX-X

# Sentry (if configured)
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
```

## Performance Optimization

### 1. Enable Static Exports (if no dynamic features):
```javascript
// next.config.ts
const nextConfig = {
  output: 'export',
  // ... other config
}
```

### 2. Image Optimization:
- Use Next.js Image component
- Configure external image domains:
```javascript
const nextConfig = {
  images: {
    domains: ['your-cdn.com'],
  },
}
```

### 3. Enable Compression:
```bash
npm install compression
```

### 4. CDN Configuration:
- Static assets: Use Cloudflare, AWS CloudFront
- API caching: Configure appropriate cache headers

## Monitoring & Logging

### 1. Application Monitoring:
```bash
# Install monitoring packages
npm install @sentry/nextjs
```

### 2. Health Checks:
Create `/app/api/health/route.ts`:
```typescript
export async function GET() {
  return Response.json({ status: 'healthy' })
}
```

### 3. Logging:
```bash
# View PM2 logs
pm2 logs dashboard

# Docker logs
docker logs -f dashboard-container
```

## Security Considerations

### 1. Environment Variables:
- Never commit `.env.local` to git
- Use secrets management in production
- Rotate API keys regularly

### 2. Headers Security:
```javascript
// next.config.ts
const securityHeaders = [
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  }
]

const nextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ]
  },
}
```

### 3. Rate Limiting:
Implement rate limiting on the API side to prevent abuse.

## Troubleshooting

### Common Issues:

1. **Build Failures:**
   ```bash
   # Clear cache and rebuild
   rm -rf .next node_modules
   npm ci
   npm run build
   ```

2. **API Connection Issues:**
   - Verify NEXT_PUBLIC_API_URL is correct
   - Check CORS settings on API
   - Ensure API is accessible from deployment environment

3. **Memory Issues:**
   ```bash
   # Increase Node.js memory
   NODE_OPTIONS="--max-old-space-size=4096" npm run build
   ```

4. **Port Conflicts:**
   ```bash
   # Change port
   PORT=3001 npm start
   ```

## Backup & Recovery

### Database Backups:
```bash
# PostgreSQL backup
pg_dump -U username -h localhost dbname > backup.sql

# Restore
psql -U username -h localhost dbname < backup.sql
```

### Application Backups:
- Use Git tags for versioning
- Keep previous Docker images
- Maintain rollback procedures

## Scaling Considerations

### Horizontal Scaling:
- Use load balancer (Nginx, HAProxy)
- Deploy multiple instances
- Share session state (Redis)

### Vertical Scaling:
- Increase server resources
- Optimize Node.js performance
- Use CDN for static assets

## CI/CD Pipeline

### GitHub Actions Example:
```yaml
name: Deploy Dashboard

on:
  push:
    branches: [main]
    paths:
      - 'src/presentation/web-dashboard-next/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          
      - name: Install dependencies
        working-directory: ./src/presentation/web-dashboard-next
        run: npm ci
        
      - name: Build
        working-directory: ./src/presentation/web-dashboard-next
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
          
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          working-directory: ./src/presentation/web-dashboard-next
```

## Maintenance

### Regular Updates:
```bash
# Update dependencies
npm update
npm audit fix

# Update Next.js
npm install next@latest react@latest react-dom@latest
```

### Performance Monitoring:
- Use Lighthouse for performance audits
- Monitor Core Web Vitals
- Track API response times

---

*For more information, consult the [Next.js deployment documentation](https://nextjs.org/docs/deployment)*