"""Base classes for domain entities and value objects."""

from abc import ABC
from typing import Any, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Entity(ABC):
    """Base class for all domain entities."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class AggregateRoot(Entity):
    """Base class for aggregate roots."""
    
    _domain_events: List[Any] = field(default_factory=list, init=False)
    
    def add_domain_event(self, event: Any) -> None:
        """Add a domain event to the aggregate."""
        self._domain_events.append(event)
    
    def collect_events(self) -> List[Any]:
        """Collect and clear all domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


@dataclass(frozen=True)
class ValueObject(ABC):
    """Base class for value objects."""
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))