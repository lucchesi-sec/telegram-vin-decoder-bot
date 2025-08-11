import logging
import os
from dataclasses import dataclass


@dataclass
class Settings:
    telegram_bot_token: str
    autodev_api_key: str = ""  # Optional Auto.dev API key for default use
    http_timeout_seconds: int = 15
    log_level: str = "INFO"
    redis_url: str = ""  # deprecated; use Upstash REST env vars
    redis_ttl_seconds: int = 86400  # 24 hours default


def load_settings() -> Settings:
    # Support .env if present
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
    except Exception:
        pass

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    autodev_api_key = os.getenv("AUTODEV_API_KEY", "").strip()
    timeout = int(os.getenv("HTTP_TIMEOUT_SECONDS", "15") or 15)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    redis_url = os.getenv("REDIS_URL", "").strip()  # deprecated; unused when Upstash is configured
    redis_ttl = int(os.getenv("REDIS_TTL_SECONDS", "86400") or 86400)

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required (set in .env)")

    # Apply logging level early
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    return Settings(
        telegram_bot_token=token,
        autodev_api_key=autodev_api_key,
        http_timeout_seconds=timeout,
        log_level=log_level,
        redis_url=redis_url,
        redis_ttl_seconds=redis_ttl,
    )

