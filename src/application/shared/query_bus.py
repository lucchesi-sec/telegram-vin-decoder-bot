"""Query bus for handling queries."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

Query = TypeVar('Query')
QueryResult = TypeVar('QueryResult')


class QueryHandler(ABC, Generic[Query, QueryResult]):
    """Base class for query handlers."""
    
    @abstractmethod
    async def handle(self, query: Query) -> QueryResult:
        """Handle a query."""
        pass


class QueryBus(ABC):
    """Interface for query bus."""
    
    @abstractmethod
    async def send(self, query: Any) -> Any:
        """Send a query to be handled."""
        pass