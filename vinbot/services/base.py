"""Base service class for business logic services."""

from abc import ABC
from typing import Optional, Any, Dict
import logging


class Service(ABC):
    """Base class for all services."""
    
    def __init__(self, dependencies: Optional[Dict[str, Any]] = None):
        """Initialize the service with optional dependencies.
        
        Args:
            dependencies: Dictionary of service dependencies
        """
        self._dependencies = dependencies or {}
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def get_dependency(self, name: str) -> Any:
        """Get a dependency by name.
        
        Args:
            name: The name of the dependency
            
        Returns:
            The dependency object
            
        Raises:
            KeyError: If the dependency is not found
        """
        if name not in self._dependencies:
            raise KeyError(f"Dependency '{name}' not found in {self.__class__.__name__}")
        return self._dependencies[name]
    
    def has_dependency(self, name: str) -> bool:
        """Check if a dependency exists.
        
        Args:
            name: The name of the dependency
            
        Returns:
            True if the dependency exists
        """
        return name in self._dependencies
    
    def set_dependency(self, name: str, value: Any) -> None:
        """Set a dependency.
        
        Args:
            name: The name of the dependency
            value: The dependency object
        """
        self._dependencies[name] = value