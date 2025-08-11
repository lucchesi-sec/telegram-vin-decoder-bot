"""User domain events."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
from src.domain.shared.domain_event import DomainEvent


@dataclass
class UserCreatedEvent(DomainEvent):
    """Event raised when a new user is created."""
    
    user_id: str = ""
    telegram_id: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Set aggregate_id from user_id."""
        if not self.aggregate_id and self.user_id:
            self.aggregate_id = self.user_id
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "user.created"


@dataclass
class UserPreferencesUpdatedEvent(DomainEvent):
    """Event raised when user preferences are updated."""
    
    user_id: str = ""
    old_preferences: Dict[str, Any] = field(default_factory=dict)
    new_preferences: Dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Set aggregate_id from user_id."""
        if not self.aggregate_id and self.user_id:
            self.aggregate_id = self.user_id
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "user.preferences_updated"


@dataclass
class UserDeactivatedEvent(DomainEvent):
    """Event raised when a user is deactivated."""
    
    user_id: str = ""
    telegram_id: int = 0
    deactivated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Set aggregate_id from user_id."""
        if not self.aggregate_id and self.user_id:
            self.aggregate_id = self.user_id
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "user.deactivated"


@dataclass
class UserReactivatedEvent(DomainEvent):
    """Event raised when a user is reactivated."""
    
    user_id: str = ""
    telegram_id: int = 0
    reactivated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Set aggregate_id from user_id."""
        if not self.aggregate_id and self.user_id:
            self.aggregate_id = self.user_id
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "user.reactivated"


@dataclass
class UserVehicleSavedEvent(DomainEvent):
    """Event raised when a user saves a vehicle."""
    
    user_id: str = ""
    vin: str = ""
    saved_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Set aggregate_id from user_id."""
        if not self.aggregate_id and self.user_id:
            self.aggregate_id = self.user_id
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "user.vehicle_saved"


@dataclass
class UserSearchPerformedEvent(DomainEvent):
    """Event raised when a user performs a VIN search."""
    
    user_id: str = ""
    vin: str = ""
    service_used: str = ""
    searched_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Set aggregate_id from user_id."""
        if not self.aggregate_id and self.user_id:
            self.aggregate_id = self.user_id
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "user.search_performed"