FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose health check port for Fly.io smoke tests
EXPOSE 8080

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

# Copy env at runtime via --env-file; don't bake secrets into image

CMD ["./entrypoint.sh"]
