"""Dependency injection container."""

import logging
from dependency_injector import containers, providers
from src.config.settings import Settings
from src.infrastructure.external_services.nhtsa.nhtsa_client import NHTSAClient
from src.infrastructure.external_services.nhtsa.nhtsa_adapter import NHTSAAdapter
from src.infrastructure.external_services.autodev.autodev_client import AutoDevClient
from src.infrastructure.external_services.autodev.autodev_adapter import AutoDevAdapter
from src.infrastructure.external_services.decoder_factory import DecoderFactory
from src.infrastructure.persistence.repositories.in_memory_vehicle_repository import InMemoryVehicleRepository
from src.infrastructure.persistence.repositories.in_memory_user_repository import InMemoryUserRepository
from src.application.shared.simple_command_bus import SimpleCommandBus
from src.application.shared.simple_query_bus import SimpleQueryBus
from src.application.shared.simple_event_bus import SimpleEventBus
from src.application.vehicle.commands.handlers.decode_vin_handler import DecodeVINHandler
from src.application.vehicle.queries.handlers.get_vehicle_history_handler import GetVehicleHistoryHandler
from src.application.vehicle.services.vehicle_application_service import VehicleApplicationService
from src.application.user.services.user_application_service import UserApplicationService
from src.presentation.telegram_bot.adapters.message_adapter import MessageAdapter
from src.presentation.telegram_bot.adapters.keyboard_adapter import KeyboardAdapter


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""
    
    # Configuration
    config = providers.Configuration()
    
    # Settings
    settings = providers.Singleton(
        Settings
    )
    
    # Initialize configuration from settings
    @providers.Factory
    def config_initializer(settings=settings):
        """Initialize config from settings."""
        config.from_dict({
            'telegram': settings.telegram.model_dump(),
            'decoder': settings.decoder.model_dump(),
            'cache': settings.cache.model_dump()
        })
        return config
    
    # External Services - NHTSA
    nhtsa_client = providers.Singleton(
        NHTSAClient,
        timeout=providers.Factory(lambda s: s.decoder.timeout, settings)
    )
    
    # External Services - AutoDev
    autodev_client = providers.Singleton(
        AutoDevClient,
        api_key=providers.Factory(lambda s: s.decoder.autodev_api_key.get_secret_value() if s.decoder.autodev_api_key else None, settings),
        timeout=providers.Factory(lambda s: s.decoder.timeout, settings)
    )
    
    # Adapters
    nhtsa_adapter = providers.Singleton(
        NHTSAAdapter,
        client=nhtsa_client
    )
    
    autodev_adapter = providers.Singleton(
        AutoDevAdapter,
        client=autodev_client
    )
    
    # Decoder Factory
    decoder_factory = providers.Singleton(
        DecoderFactory,
        nhtsa_adapter=nhtsa_adapter,
        autodev_adapter=autodev_adapter
    )
    
    # Repositories
    vehicle_repository = providers.Singleton(
        InMemoryVehicleRepository
    )
    
    user_repository = providers.Singleton(
        InMemoryUserRepository
    )
    
    # Event Bus
    event_bus = providers.Singleton(
        SimpleEventBus
    )
    
    # Command and Query Handlers
    decode_vin_handler = providers.Factory(
        DecodeVINHandler,
        vehicle_repo=vehicle_repository,
        decoder_factory=decoder_factory,
        event_bus=event_bus,
        logger=providers.Factory(lambda: logging.getLogger('decode_vin_handler'))
    )
    
    get_vehicle_history_handler = providers.Factory(
        GetVehicleHistoryHandler,
        vehicle_repo=vehicle_repository,
        logger=providers.Factory(lambda: logging.getLogger('get_vehicle_history_handler'))
    )
    
    # Command and Query Buses
    command_bus = providers.Singleton(
        SimpleCommandBus
    )
    
    query_bus = providers.Singleton(
        SimpleQueryBus
    )
    
    # Application Services
    vehicle_application_service = providers.Factory(
        VehicleApplicationService,
        command_bus=command_bus,
        query_bus=query_bus,
        logger=providers.Factory(lambda: logging.getLogger('vehicle_application_service'))
    )
    
    user_application_service = providers.Factory(
        UserApplicationService,
        user_repository=user_repository,
        event_bus=event_bus,
        logger=providers.Factory(lambda: logging.getLogger('user_application_service'))
    )
    
    # Presentation Layer Adapters
    message_adapter = providers.Singleton(
        MessageAdapter
    )
    
    keyboard_adapter = providers.Singleton(
        KeyboardAdapter
    )