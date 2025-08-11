"""Unit of work pattern implementation."""

from abc import ABC, abstractmethod
from typing import AsyncContextManager


class UnitOfWork(ABC):
    """Interface for unit of work pattern."""
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit the unit of work."""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the unit of work."""
        pass


class UnitOfWorkManager(ABC):
    """Interface for unit of work manager."""
    
    @abstractmethod
    def create(self) -> AsyncContextManager[UnitOfWork]:
        """Create a new unit of work."""
        pass