"""Database base configuration for SQLAlchemy models."""

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, Optional
import os


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


class DatabaseEngine:
    """Database engine management."""
    
    def __init__(
        self, 
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_pre_ping: bool = True,
        pool_recycle: int = 1800,
        pool_timeout: int = 30,
        echo_sql: bool = False
    ):
        """Initialize database engine with optimized pooling.
        
        Args:
            database_url: PostgreSQL connection URL
            pool_size: Number of connections to maintain
            max_overflow: Maximum overflow connections allowed
            pool_pre_ping: Test connections before using
            pool_recycle: Time before connection recycle
            pool_timeout: Timeout for getting connection
            echo_sql: Whether to echo SQL statements
        """
        self.engine = create_async_engine(
            database_url,
            echo=echo_sql or os.getenv("ENVIRONMENT", "production") == "development",
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            pool_recycle=pool_recycle,
            pool_timeout=pool_timeout
        )
        
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session.
        
        Yields:
            Database session
        """
        async with self.async_session_maker() as session:
            yield session
    
    async def create_all(self):
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_all(self):
        """Drop all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def dispose(self):
        """Dispose of the engine."""
        await self.engine.dispose()