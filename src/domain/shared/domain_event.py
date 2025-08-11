"""Domain event base class."""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Any, Dict
import json


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""
    
    aggregate_id: str = field(default="")
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": self.event_id,
            "occurred_at": self.occurred_at.isoformat(),
            "aggregate_id": self.aggregate_id,
            "event_type": self.__class__.__name__,
            **self.__dict__
        }