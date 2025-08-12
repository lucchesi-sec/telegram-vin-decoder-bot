FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose ports for both services
EXPOSE 8000 8080

# Install Node.js for Next.js dashboard
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
COPY entrypoint.sh ./
COPY web-entrypoint.sh ./
COPY main.py ./

RUN chmod +x entrypoint.sh web-entrypoint.sh

# Copy env at runtime via --env-file; don't bake secrets into image

# Build Next.js app
WORKDIR /app/web-dashboard-next
COPY src/presentation/web-dashboard-next/package*.json ./
RUN npm ci --only=production
COPY src/presentation/web-dashboard-next/ ./
RUN npm run build

# Return to main app directory
WORKDIR /app

# Default command will be overridden by fly.toml processes
CMD ["./entrypoint.sh"]
