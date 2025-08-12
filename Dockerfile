FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose ports for both services
EXPOSE 8000 8080

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
COPY entrypoint.sh ./
COPY main.py ./

RUN chmod +x entrypoint.sh

# Copy env at runtime via --env-file; don't bake secrets into image

# Build Next.js app
WORKDIR /app/web-dashboard-next
COPY web-dashboard-next/package*.json ./
RUN npm ci --only=production
COPY web-dashboard-next/ ./
RUN npm run build

# Return to main app directory
WORKDIR /app

# Default command will be overridden by fly.toml processes
CMD ["./entrypoint.sh"]
