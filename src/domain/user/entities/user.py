"""User domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from src.domain.shared.entity import AggregateRoot
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.domain.user.events.user_events import UserCreatedEvent, UserPreferencesUpdatedEvent


@dataclass
class UserHistory:
    """Represents a user's VIN decode history entry."""
    
    vin: str = ""
    decoded_at: datetime = field(default_factory=datetime.utcnow)
    service_used: str = ""
    vehicle_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class User(AggregateRoot):
    """User aggregate root."""
    
    telegram_id: TelegramID = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferences: UserPreferences = field(default_factory=UserPreferences)
    history: List[UserHistory] = field(default_factory=list)
    saved_vehicles: List[str] = field(default_factory=list)  # List of VINs
    is_active: bool = True
    last_activity: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize the user aggregate."""
        # Initialize domain events list if not already done
        if not hasattr(self, '_domain_events'):
            self._domain_events = []
        if not self.last_activity:
            self.last_activity = datetime.utcnow()
    
    @classmethod
    def create(
        cls,
        telegram_id: TelegramID,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        preferences: Optional[UserPreferences] = None
    ) -> 'User':
        """Factory method for creating a new user."""
        user = cls(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            preferences=preferences or UserPreferences()
        )
        
        # Emit domain event
        user.add_domain_event(UserCreatedEvent(
            user_id=user.id,
            telegram_id=telegram_id.value,
            created_at=datetime.utcnow()
        ))
        
        return user
    
    def update_preferences(self, new_preferences: UserPreferences) -> None:
        """Update user preferences."""
        old_preferences = self.preferences
        self.preferences = new_preferences
        self.updated_at = datetime.utcnow()
        
        # Emit domain event
        self.add_domain_event(UserPreferencesUpdatedEvent(
            user_id=self.id,
            old_preferences=old_preferences.to_dict(),
            new_preferences=new_preferences.to_dict(),
            updated_at=self.updated_at
        ))
    
    def add_to_history(
        self,
        vin: str,
        service_used: str,
        vehicle_info: Dict[str, Any]
    ) -> None:
        """Add a VIN decode to user's history."""
        history_entry = UserHistory(
            vin=vin,
            decoded_at=datetime.utcnow(),
            service_used=service_used,
            vehicle_info=vehicle_info
        )
        self.history.append(history_entry)
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Limit history to last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def save_vehicle(self, vin: str) -> None:
        """Save a vehicle to the user's saved vehicles."""
        if vin not in self.saved_vehicles:
            self.saved_vehicles.append(vin)
            self.updated_at = datetime.utcnow()
    
    def remove_saved_vehicle(self, vin: str) -> bool:
        """Remove a vehicle from the user's saved vehicles."""
        if vin in self.saved_vehicles:
            self.saved_vehicles.remove(vin)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_recent_history(self, limit: int = 10) -> List[UserHistory]:
        """Get recent history entries."""
        return self.history[-limit:] if self.history else []
    
    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def reactivate(self) -> None:
        """Reactivate the user."""
        self.is_active = True
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @property
    def display_name(self) -> str:
        """Get user's display name."""
        if self.first_name:
            return self.first_name
        if self.username:
            return f"@{self.username}"
        return f"User {self.telegram_id.value}"