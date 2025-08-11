import asyncio
from logging.config import fileConfig
import os
import sys
from pathlib import Path
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models here
from src.infrastructure.persistence.models import Base
target_metadata = Base.metadata

def prepare_async_database_url(url):
    """Prepare database URL for async connections with asyncpg."""
    if not url:
        return url
    
    # Convert to async driver
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return url

if os.getenv("DATABASE_URL"):
    # Preserve any query parameters (e.g., sslmode) provided via env var
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def _strip_sslmode_and_build_connect_args(url: str) -> tuple[str, dict]:
    """Remove unsupported 'sslmode' param for asyncpg and map to connect_args.

    asyncpg.connect() does not accept 'sslmode'. We translate common values:
    - disable -> ssl=None (no TLS)
    - anything else -> ssl=True (use default TLS context)
    All query parameters are stripped from the URL to avoid unknown kwargs.
    """
    parsed = urlparse(url)
    query_map = parse_qs(parsed.query, keep_blank_values=True)

    connect_args: dict = {}
    sslmode_values = query_map.pop("sslmode", None)
    if sslmode_values:
        mode = (sslmode_values[-1] or "").lower()
        if mode == "disable":
            connect_args["ssl"] = None
        else:
            # Treat require/verify-* as True. For stricter verification,
            # supply an SSLContext in application settings if needed.
            connect_args["ssl"] = True

    # If connecting to Fly's internal network Postgres and no explicit sslmode was set,
    # default to no TLS (servers there typically don't speak TLS on internal address).
    hostname = parsed.hostname or ""
    if "ssl" not in connect_args and hostname.endswith(".internal"):
        connect_args["ssl"] = None

    connect_args: dict = {}
    
    # Handle SSL configuration for Fly.io
    hostname = parsed.hostname or ""
    
    # For Fly.io internal connections (.internal suffix) or localhost: always disable SSL
    if hostname.endswith(".internal") or hostname in ["localhost", "127.0.0.1"]:
        connect_args["ssl"] = None
    else:
        # For external connections: use SSL by default unless explicitly disabled
        sslmode_values = query_map.pop("sslmode", None)
        if sslmode_values:
            mode = (sslmode_values[-1] or "").lower()
            if mode in ["disable", "allow"]:
                connect_args["ssl"] = None
            else:
                # require, verify-ca, verify-full
                connect_args["ssl"] = True
        elif os.getenv("ENVIRONMENT") == "production":
            # Default to SSL enabled for production external connections
            connect_args["ssl"] = True
        else:
            # Default to SSL disabled for development/unknown environments
            connect_args["ssl"] = None

    # Drop all query parameters to prevent SQLAlchemy from passing them
    new_url = urlunparse(parsed._replace(query=""))
    return new_url, connect_args


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async support."""
    
    from sqlalchemy.ext.asyncio import create_async_engine
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get URL from environment variable or config file and convert to async
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    
    # Prepare for async connection and map sslmode to connect args
    url = prepare_async_database_url(url)
    url, connect_args = _strip_sslmode_and_build_connect_args(url)
    
    # Log connection details (without password)
    parsed_url = urlparse(url)
    safe_url = f"{parsed_url.scheme}://{parsed_url.username}@{parsed_url.hostname}:{parsed_url.port}{parsed_url.path}"
    logger.info(f"Connecting to database: {safe_url}")
    logger.info(f"SSL configuration: {connect_args}")
    
    # Add timeout to connect_args for asyncpg
    connect_args['timeout'] = 30  # 30 second timeout for slow networks
    
    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    try:
        async with connectable.connect() as connection:
            logger.info("Database connection established, running migrations...")
            await connection.run_sync(do_run_migrations)
            logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    finally:
        await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
