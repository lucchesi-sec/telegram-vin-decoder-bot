"""Application settings."""

from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Optional


class TelegramSettings(BaseSettings):
    """Telegram bot settings."""

    bot_token: SecretStr = Field(..., alias="TELEGRAM_BOT_TOKEN")
    webhook_url: Optional[str] = Field(None, alias="TELEGRAM_WEBHOOK_URL")
    max_connections: int = Field(default=40, alias="TELEGRAM_MAX_CONNECTIONS")

    # Additional fields from environment
    carsxe_api_key: Optional[str] = Field(None, alias="CARSXE_API_KEY")
    fly_api_token: Optional[SecretStr] = Field(None, alias="FLY_API_TOKEN")
    autodev_api_key: Optional[str] = Field(None, alias="AUTODEV_API_KEY")
    upstash_redis_rest_url: Optional[str] = Field(None, alias="UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: Optional[SecretStr] = Field(None, alias="UPSTASH_REDIS_REST_TOKEN")
    http_timeout_seconds: Optional[int] = Field(default=15, alias="HTTP_TIMEOUT_SECONDS")
    log_level: Optional[str] = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields


class CacheSettings(BaseSettings):
    """Cache settings."""

    redis_url: Optional[str] = Field(None, alias="REDIS_URL")
    upstash_url: Optional[str] = Field(None, alias="UPSTASH_REDIS_REST_URL")
    upstash_token: Optional[SecretStr] = Field(None, alias="UPSTASH_REDIS_REST_TOKEN")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")

    class Config:
        env_file = ".env"
        extra = "ignore"


class DecoderSettings(BaseSettings):
    """VIN decoder settings."""

    nhtsa_api_key: Optional[SecretStr] = Field(None, alias="NHTSA_API_KEY")
    autodev_api_key: Optional[SecretStr] = Field(None, alias="AUTODEV_API_KEY")
    default_service: str = Field(default="autodev", alias="DEFAULT_DECODER_SERVICE")
    cache_ttl: int = Field(default=3600, alias="DECODER_CACHE_TTL")
    timeout: int = Field(default=30, alias="DECODER_TIMEOUT")

    class Config:
        env_file = ".env"
        extra = "ignore"


class DatabaseSettings(BaseSettings):
    """Database settings."""

    database_url: Optional[str] = Field(None, alias="DATABASE_URL")
    pool_size: int = Field(default=20, alias="DB_POOL_SIZE")
    max_overflow: int = Field(
        default=10, alias="DB_MAX_OVERFLOW"
    )  # Allow overflow for burst traffic
    pool_recycle: int = Field(
        default=1800, alias="DB_POOL_RECYCLE"
    )  # Recycle connections every 30 min
    pool_pre_ping: bool = Field(
        default=True, alias="DB_POOL_PRE_PING"
    )  # Test connections before using
    pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")  # Timeout for getting connection
    echo_sql: bool = Field(default=False, alias="DB_ECHO_SQL")

    class Config:
        env_file = ".env"
        extra = "ignore"


class Settings(BaseSettings):
    """Application settings."""

    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    decoder: DecoderSettings = Field(default_factory=DecoderSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        extra = "ignore"
