"""User domain events."""

from .user_events import (
    UserCreatedEvent,
    UserPreferencesUpdatedEvent,
    UserDeactivatedEvent,
    UserReactivatedEvent,
    UserVehicleSavedEvent,
    UserSearchPerformedEvent
)

__all__ = [
    'UserCreatedEvent',
    'UserPreferencesUpdatedEvent',
    'UserDeactivatedEvent', 
    'UserReactivatedEvent',
    'UserVehicleSavedEvent',
    'UserSearchPerformedEvent'
]