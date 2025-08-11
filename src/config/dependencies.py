"""Dependency injection container."""

import logging
from typing import Optional
from dependency_injector import containers, providers

logger = logging.getLogger(__name__)
from src.config.settings import Settings
from src.infrastructure.external_services.nhtsa.nhtsa_client import NHTSAClient
from src.infrastructure.external_services.nhtsa.nhtsa_adapter import NHTSAAdapter
from src.infrastructure.external_services.autodev.autodev_client import AutoDevClient
from src.infrastructure.external_services.autodev.autodev_adapter import AutoDevAdapter
from src.infrastructure.external_services.decoder_factory import DecoderFactory
from src.infrastructure.persistence.repositories.in_memory_vehicle_repository import InMemoryVehicleRepository
from src.infrastructure.persistence.repositories.in_memory_user_repository import InMemoryUserRepository
from src.infrastructure.persistence.repositories.postgresql_user_repository import PostgreSQLUserRepository
from src.infrastructure.persistence.repositories.postgresql_vehicle_repository import PostgreSQLVehicleRepository
from src.infrastructure.persistence.models import DatabaseEngine
from src.infrastructure.persistence.cache import UpstashCache, VehicleCacheRepository
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
    
    # External Services - NHTSA
    nhtsa_client = providers.Singleton(
        NHTSAClient,
        timeout=providers.Factory(lambda: Container.settings().decoder.timeout)
    )
    
    # External Services - AutoDev
    autodev_client = providers.Singleton(
        lambda: AutoDevClient(
            api_key=Container.settings().decoder.autodev_api_key.get_secret_value() if Container.settings().decoder.autodev_api_key else None,
            timeout=Container.settings().decoder.timeout
        )
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
    
    # Database Engine (conditional)
    database_engine = providers.Singleton(
        lambda: DatabaseEngine(
            Container.settings().database.database_url.replace("postgresql://", "postgresql+asyncpg://", 1) 
            if Container.settings().database.database_url.startswith("postgresql://") 
            else Container.settings().database.database_url
        ) if Container.settings().database.database_url else None
    )
    
    # Cache (conditional)
    upstash_cache = providers.Singleton(
        lambda: UpstashCache(
            redis_url=Container.settings().cache.upstash_url,
            redis_token=Container.settings().cache.upstash_token.get_secret_value()
        ) if Container.settings().cache.upstash_url and Container.settings().cache.upstash_token else None
    )
    
    vehicle_cache_repository = providers.Singleton(
        lambda: VehicleCacheRepository(Container.upstash_cache()) if Container.upstash_cache() else None
    )
    
    # Repositories (conditional based on database availability)
    vehicle_repository = providers.Singleton(
        lambda: PostgreSQLVehicleRepository(Container.database_engine().async_session_maker)
        if Container.database_engine() and hasattr(Container.database_engine(), 'async_session_maker')
        else InMemoryVehicleRepository()
    )
    
    user_repository = providers.Singleton(
        lambda: PostgreSQLUserRepository(Container.database_engine().async_session_maker)
        if Container.database_engine() and hasattr(Container.database_engine(), 'async_session_maker')
        else InMemoryUserRepository()
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
    
    @staticmethod
    async def initialize_database(container):
        """Initialize database if configured."""
        engine = container.database_engine()
        if engine:
            logger.info("Initializing database...")
            try:
                # Create tables if they don't exist
                await engine.create_all()
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                raise
    
    @staticmethod
    def bootstrap(container):
        """Bootstrap the container by registering handlers with buses."""
        from src.application.vehicle.commands import DecodeVINCommand, GetVehicleHistoryQuery
        
        # Get bus instances
        command_bus = container.command_bus()
        query_bus = container.query_bus()
        
        # Register command handlers
        decode_vin_handler = container.decode_vin_handler()
        command_bus.register_handler(DecodeVINCommand, decode_vin_handler)
        
        # Register query handlers
        get_vehicle_history_handler = container.get_vehicle_history_handler()
        query_bus.register_handler(GetVehicleHistoryQuery, get_vehicle_history_handler)
        
        logging.getLogger(__name__).info("Handlers registered with buses")