"""User application service."""

import logging
from typing import Optional, List, Dict, Any
from src.domain.user.entities.user import User
from src.domain.user.repositories.user_repository import UserRepository
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.application.shared.event_bus import EventBus


class UserApplicationService:
    """Application service for user management."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        event_bus: EventBus,
        logger: logging.Logger
    ):
        """Initialize user application service.
        
        Args:
            user_repository: Repository for user persistence
            event_bus: Event bus for domain events
            logger: Logger instance
        """
        self.user_repository = user_repository
        self.event_bus = event_bus
        self.logger = logger
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Get existing user or create new one.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            User instance
        """
        tid = TelegramID(telegram_id)
        
        # Check if user exists
        existing_user = await self.user_repository.get_by_telegram_id(tid)
        if existing_user:
            # Update user info if changed
            updated = False
            if username and existing_user.username != username:
                existing_user.username = username
                updated = True
            if first_name and existing_user.first_name != first_name:
                existing_user.first_name = first_name
                updated = True
            if last_name and existing_user.last_name != last_name:
                existing_user.last_name = last_name
                updated = True
            
            if updated:
                await self.user_repository.save(existing_user)
            
            return existing_user
        
        # Create new user
        new_user = User.create(
            telegram_id=tid,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        await self.user_repository.save(new_user)
        
        # Publish domain events
        events = new_user.collect_events()
        for event in events:
            await self.event_bus.publish(event)
        
        self.logger.info(f"Created new user: {new_user.display_name}")
        
        return new_user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User if found, None otherwise
        """
        tid = TelegramID(telegram_id)
        return await self.user_repository.get_by_telegram_id(tid)
    
    async def update_user_preferences(
        self,
        telegram_id: int,
        preferences: Dict[str, Any]
    ) -> Optional[User]:
        """Update user preferences.
        
        Args:
            telegram_id: Telegram user ID
            preferences: New preferences dict
            
        Returns:
            Updated user if found, None otherwise
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        # Create new preferences from dict
        new_prefs = UserPreferences.from_dict(preferences)
        user.update_preferences(new_prefs)
        
        await self.user_repository.save(user)
        
        # Publish domain events
        events = user.collect_events()
        for event in events:
            await self.event_bus.publish(event)
        
        self.logger.info(f"Updated preferences for user: {user.display_name}")
        
        return user
    
    async def set_preferred_service(
        self,
        telegram_id: int,
        service: str
    ) -> Optional[User]:
        """Set user's preferred decoder service.
        
        Args:
            telegram_id: Telegram user ID
            service: Service name (nhtsa or autodev)
            
        Returns:
            Updated user if found, None otherwise
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        # Update service preference
        new_prefs = user.preferences.with_decoder(service.lower())
        user.update_preferences(new_prefs)
        
        await self.user_repository.save(user)
        
        # Publish domain events
        events = user.collect_events()
        for event in events:
            await self.event_bus.publish(event)
        
        self.logger.info(f"Set preferred decoder to {service} for user: {user.display_name}")
        
        return user
    
    async def add_to_user_history(
        self,
        telegram_id: int,
        vin: str,
        service_used: str,
        vehicle_info: Dict[str, Any]
    ) -> Optional[User]:
        """Add VIN decode to user's history.
        
        Args:
            telegram_id: Telegram user ID
            vin: Vehicle VIN
            service_used: Decoder service used
            vehicle_info: Decoded vehicle information
            
        Returns:
            Updated user if found, None otherwise
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        user.add_to_history(vin, service_used, vehicle_info)
        await self.user_repository.save(user)
        
        self.logger.debug(f"Added VIN {vin} to history for user: {user.display_name}")
        
        return user
    
    async def save_user_vehicle(
        self,
        telegram_id: int,
        vin: str
    ) -> Optional[User]:
        """Save a vehicle to user's saved vehicles.
        
        Args:
            telegram_id: Telegram user ID
            vin: Vehicle VIN to save
            
        Returns:
            Updated user if found, None otherwise
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        user.save_vehicle(vin)
        await self.user_repository.save(user)
        
        self.logger.info(f"Saved VIN {vin} for user: {user.display_name}")
        
        return user
    
    async def remove_saved_vehicle(
        self,
        telegram_id: int,
        vin: str
    ) -> Optional[bool]:
        """Remove a vehicle from user's saved vehicles.
        
        Args:
            telegram_id: Telegram user ID
            vin: Vehicle VIN to remove
            
        Returns:
            True if removed, False if not found, None if user not found
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        removed = user.remove_saved_vehicle(vin)
        if removed:
            await self.user_repository.save(user)
            self.logger.info(f"Removed VIN {vin} for user: {user.display_name}")
        
        return removed
    
    async def get_user_history(
        self,
        telegram_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's recent VIN decode history.
        
        Args:
            telegram_id: Telegram user ID
            limit: Maximum number of entries to return
            
        Returns:
            List of history entries
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return []
        
        history = user.get_recent_history(limit)
        return [
            {
                "vin": entry.vin,
                "decoded_at": entry.decoded_at.isoformat(),
                "service_used": entry.service_used,
                "vehicle_info": entry.vehicle_info
            }
            for entry in history
        ]
    
    async def deactivate_user(self, telegram_id: int) -> Optional[User]:
        """Deactivate a user.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            Deactivated user if found, None otherwise
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        user.deactivate()
        await self.user_repository.save(user)
        
        self.logger.info(f"Deactivated user: {user.display_name}")
        
        return user