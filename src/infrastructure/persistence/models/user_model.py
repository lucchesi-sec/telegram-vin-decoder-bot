"""SQLAlchemy User model."""

from sqlalchemy import Column, String, BigInteger, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .base import Base


class SubscriptionTier(enum.Enum):
    """User subscription tiers."""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class UserModel(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    subscription_tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    
    preferences = Column(JSON, default=dict)
    
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"