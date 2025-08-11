"""PostgreSQL user repository implementation."""

import logging
import uuid
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.user.entities.user import User
from src.domain.user.repositories.user_repository import UserRepository
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.infrastructure.persistence.models import UserModel, SubscriptionTier
from datetime import datetime


logger = logging.getLogger(__name__)


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL implementation of user repository."""
    
    def __init__(self, session_factory):
        """Initialize the repository.
        
        Args:
            session_factory: SQLAlchemy async session factory
        """
        self.session_factory = session_factory
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by internal ID.
        
        Args:
            user_id: Internal user ID
            
        Returns:
            User if found, None otherwise
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()
            
            if user_model:
                return self._to_domain(user_model)
            return None
    
    async def get_by_telegram_id(self, telegram_id: TelegramID) -> Optional[User]:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User if found, None otherwise
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.telegram_id == telegram_id.value)
            )
            user_model = result.scalar_one_or_none()
            
            if user_model:
                return self._to_domain(user_model)
            return None
    
    async def save(self, user: User) -> None:
        """Save or update a user.
        
        Args:
            user: User to save
        """
        async with self.session_factory() as session:
            # Check if user exists
            result = await session.execute(
                select(UserModel).where(UserModel.id == user.id)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing user
                await session.execute(
                    update(UserModel)
                    .where(UserModel.id == user.id)
                    .values(
                        telegram_id=user.telegram_id.value,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        language_code=user.language_code,
                        is_active=user.is_active,
                        is_premium=user.is_premium,
                        subscription_tier=self._get_subscription_tier(user),
                        preferences=user.preferences.to_dict() if user.preferences else {},
                        last_active_at=user.last_active_at,
                        updated_at=datetime.utcnow()
                    )
                )
            else:
                # Create new user
                user_model = UserModel(
                    id=user.id,
                    telegram_id=user.telegram_id.value,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    language_code=user.language_code,
                    is_active=user.is_active,
                    is_premium=user.is_premium,
                    subscription_tier=self._get_subscription_tier(user),
                    preferences=user.preferences.to_dict() if user.preferences else {},
                    last_active_at=user.last_active_at,
                    created_at=user.created_at
                )
                session.add(user_model)
            
            await session.commit()
            logger.info(f"Saved user: {user.id}")
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: Internal user ID
            
        Returns:
            True if deleted, False if not found
        """
        async with self.session_factory() as session:
            result = await session.execute(
                delete(UserModel).where(UserModel.id == user_id)
            )
            await session.commit()
            
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Deleted user: {user_id}")
            
            return deleted
    
    async def list_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List active users.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of active users
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserModel)
                .where(UserModel.is_active == True)
                .order_by(UserModel.last_active_at.desc())
                .limit(limit)
                .offset(offset)
            )
            user_models = result.scalars().all()
            
            return [self._to_domain(model) for model in user_models]
    
    async def exists_by_telegram_id(self, telegram_id: TelegramID) -> bool:
        """Check if user exists by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            True if user exists, False otherwise
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count())
                .select_from(UserModel)
                .where(UserModel.telegram_id == telegram_id.value)
            )
            count = result.scalar()
            return count > 0
    
    async def count_active_users(self) -> int:
        """Count active users.
        
        Returns:
            Number of active users
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count())
                .select_from(UserModel)
                .where(UserModel.is_active == True)
            )
            return result.scalar() or 0
    
    async def find_all(self) -> List[User]:
        """Find all users.
        
        Returns:
            List of all users
        """
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserModel).order_by(UserModel.created_at.desc())
            )
            user_models = result.scalars().all()
            
            return [self._to_domain(model) for model in user_models]
    
    def _to_domain(self, model: UserModel) -> User:
        """Convert database model to domain entity.
        
        Args:
            model: Database model
            
        Returns:
            Domain entity
        """
        preferences = None
        if model.preferences:
            preferences = UserPreferences.from_dict(model.preferences)
        
        return User(
            id=model.id,
            telegram_id=TelegramID(model.telegram_id),
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            language_code=model.language_code,
            is_active=model.is_active,
            is_premium=model.is_premium,
            preferences=preferences,
            last_active_at=model.last_active_at
        )
    
    def _get_subscription_tier(self, user: User) -> SubscriptionTier:
        """Get subscription tier for user.
        
        Args:
            user: User entity
            
        Returns:
            Subscription tier
        """
        if user.is_premium:
            return SubscriptionTier.PREMIUM
        return SubscriptionTier.FREE