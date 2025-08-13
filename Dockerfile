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

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src
COPY alembic ./alembic
COPY config/alembic.ini ./alembic.ini
COPY scripts/entrypoint.sh ./entrypoint.sh
COPY scripts/web-entrypoint.sh ./web-entrypoint.sh
COPY main.py ./

RUN chmod +x entrypoint.sh web-entrypoint.sh

# Build Next.js app
WORKDIR /app/src/presentation/web-dashboard-next
COPY src/presentation/web-dashboard-next/package*.json ./
RUN npm ci
COPY src/presentation/web-dashboard-next/ ./
RUN npm run build

# Remove dev dependencies to reduce size
RUN npm prune --production

# Return to main app directory
WORKDIR /app

# Default command will be overridden by fly.toml processes
CMD ["./entrypoint.sh"]