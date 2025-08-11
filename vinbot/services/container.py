"""Dependency injection container for managing services."""

import logging
from typing import Dict, Any, Optional, TypeVar, Type
from telegram.ext import ContextTypes

from .base import Service
from .vin_service import VINDecodingService
from .user_service import UserPreferencesService
from .message_service import MessageHandlingService
from .settings_service import SettingsService
from .decoder_service import DecoderSelectionService

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Service)


class ServiceContainer:
    """Container for managing service dependencies."""
    
    def __init__(self):
        """Initialize the service container."""
        self._services: Dict[str, Service] = {}
        self._initialized = False
    
    def initialize(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Initialize all services with their dependencies.
        
        Args:
            context: The bot context containing shared resources
        """
        if self._initialized:
            return
        
        # Get shared resources from context
        user_data_mgr = context.bot_data.get("user_data_manager")
        cache = context.bot_data.get("cache")
        settings = context.bot_data.get("settings")
        
        # Create decoder selection service
        decoder_service = DecoderSelectionService({
            'user_data_manager': user_data_mgr,
            'cache': cache,
            'settings': settings
        })
        self.register('decoder_service', decoder_service)
        
        # Create user preferences service
        user_service = UserPreferencesService({
            'user_data_manager': user_data_mgr
        })
        self.register('user_service', user_service)
        
        # Create VIN decoding service
        vin_service = VINDecodingService({
            'user_data_manager': user_data_mgr,
            'decoder_service': decoder_service,
            'user_service': user_service,
            'cache': cache
        })
        self.register('vin_service', vin_service)
        
        # Create message handling service
        message_service = MessageHandlingService({
            'user_service': user_service,
            'vin_service': vin_service
        })
        self.register('message_service', message_service)
        
        # Create settings service
        settings_service = SettingsService({
            'user_service': user_service,
            'settings': settings
        })
        self.register('settings_service', settings_service)
        
        self._initialized = True
        logger.info("Service container initialized with all services")
    
    def register(self, name: str, service: Service) -> None:
        """Register a service.
        
        Args:
            name: The name to register the service under
            service: The service instance
        """
        self._services[name] = service
        logger.debug(f"Registered service: {name}")
    
    def get(self, name: str) -> Optional[Service]:
        """Get a service by name.
        
        Args:
            name: The service name
            
        Returns:
            The service instance or None
        """
        return self._services.get(name)
    
    def get_typed(self, name: str, service_type: Type[T]) -> Optional[T]:
        """Get a typed service by name.
        
        Args:
            name: The service name
            service_type: The expected service type
            
        Returns:
            The typed service instance or None
        """
        service = self._services.get(name)
        if service and isinstance(service, service_type):
            return service
        return None
    
    def get_all(self) -> Dict[str, Service]:
        """Get all registered services.
        
        Returns:
            Dictionary of all services
        """
        return self._services.copy()
    
    def is_initialized(self) -> bool:
        """Check if the container is initialized.
        
        Returns:
            True if initialized
        """
        return self._initialized


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get the global service container instance.
    
    Returns:
        The service container
    """
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def initialize_services(context: ContextTypes.DEFAULT_TYPE) -> ServiceContainer:
    """Initialize the service container with context.
    
    Args:
        context: The bot context
        
    Returns:
        The initialized service container
    """
    container = get_container()
    container.initialize(context)
    return container