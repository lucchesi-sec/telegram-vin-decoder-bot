"""Pytest configuration and global fixtures."""

import asyncio
import logging
import os
import pytest
from datetime import datetime
from typing import Dict, Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

# Testing imports
import pytest_asyncio

# Application imports
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.domain.vehicle.value_objects.vin_number import VINNumber
from src.domain.vehicle.value_objects.model_year import ModelYear
from src.infrastructure.persistence.repositories.in_memory_user_repository import InMemoryUserRepository
from src.infrastructure.persistence.repositories.in_memory_vehicle_repository import InMemoryVehicleRepository

# Configure asyncio for tests
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return {
        "telegram": {
            "bot_token": "test_token",
            "webhook_url": None,
            "max_connections": 40,
            "carsxe_api_key": "test_carsxe_key",
            "autodev_api_key": "test_autodev_key",
            "http_timeout_seconds": 15,
            "log_level": "INFO"
        },
        "cache": {
            "redis_url": None,
            "upstash_url": "test_upstash_url",
            "upstash_token": "test_upstash_token",
            "cache_ttl": 3600
        },
        "decoder": {
            "nhtsa_api_key": "test_nhtsa_key",
            "autodev_api_key": "test_autodev_key",
            "default_service": "nhtsa",
            "cache_ttl": 3600,
            "timeout": 30
        }
    }


@pytest.fixture
def sample_vin():
    """Sample VIN for testing."""
    return VINNumber("1HGBH41JXMN109186")


@pytest.fixture
def sample_user_preferences():
    """Sample user preferences for testing."""
    return UserPreferences(
        preferred_decoder="nhtsa",
        include_market_value=True,
        include_history=False,
        include_recalls=True,
        include_specs=True,
        format_preference="standard"
    )


@pytest.fixture
def sample_telegram_id():
    """Sample Telegram ID for testing."""
    return TelegramID(123456789)


@pytest.fixture
def sample_user(sample_telegram_id, sample_user_preferences):
    """Sample user for testing."""
    from src.domain.user.entities.user import User
    return User.create(
        telegram_id=sample_telegram_id,
        username="testuser",
        first_name="Test",
        last_name="User",
        preferences=sample_user_preferences
    )


@pytest.fixture
async def user_repository():
    """Create an in-memory user repository for testing."""
    return InMemoryUserRepository()


@pytest.fixture
async def vehicle_repository():
    """Create an in-memory vehicle repository for testing."""
    return InMemoryVehicleRepository()


@pytest.fixture
def mock_nhtsa_response():
    """Mock NHTSA API response data."""
    return {
        "Count": 1,
        "Results": [{
            "Make": "Honda",
            "Model": "Civic",
            "ModelYear": "2021",
            "VehicleType": "PASSENGER CAR",
            "BodyClass": "Sedan/Saloon",
            "EngineModel": "L15B7",
            "EngineCylinders": "4",
            "DisplacementL": "1.5",
            "FuelTypePrimary": "Gasoline",
            "TransmissionStyle": "CVT"
        }]
    }


@pytest.fixture
def mock_autodev_response():
    """Mock AutoDev API response data."""
    return {
        "vin": "1HGBH41JXMN109186",
        "make": {"name": "Honda"},
        "model": {"name": "Civic"},
        "years": [{"year": 2021}],
        "engine": {
            "name": "1.5L I4",
            "cylinder": 4,
            "size": "1.5L",
            "fuelType": "Gasoline",
            "horsepower": 180,
            "torque": 177
        },
        "transmission": {
            "name": "CVT",
            "transmissionType": "Automatic",
            "numberOfSpeeds": "Variable"
        },
        "categories": {
            "primaryBodyType": "Sedan",
            "vehicleStyle": "4-Door Sedan",
            "epaClass": "Compact"
        }
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient for testing."""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram Bot for testing."""
    mock_bot = AsyncMock()
    mock_bot.token = "test_token"
    return mock_bot


@pytest.fixture
def mock_telegram_update():
    """Mock Telegram Update for testing."""
    mock_update = MagicMock()
    mock_update.effective_user.id = 123456789
    mock_update.effective_user.username = "testuser"
    mock_update.effective_user.first_name = "Test"
    mock_update.effective_user.last_name = "User"
    mock_update.effective_chat.id = 123456789
    mock_update.message.text = "/start"
    mock_update.message.date = datetime.utcnow()
    return mock_update


@pytest.fixture
def mock_telegram_context():
    """Mock Telegram context for testing."""
    mock_context = MagicMock()
    mock_context.bot = mock_telegram_bot
    mock_context.user_data = {}
    mock_context.chat_data = {}
    return mock_context


@pytest.fixture
def caplog_debug(caplog):
    """Configure caplog for debug level logging."""
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    test_env = {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "AUTODEV_API_KEY": "test_autodev_key",
        "NHTSA_API_KEY": "test_nhtsa_key",
        "UPSTASH_REDIS_REST_URL": "test_upstash_url",
        "UPSTASH_REDIS_REST_TOKEN": "test_upstash_token",
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG"
    }
    
    with patch.dict(os.environ, test_env):
        yield


# Async fixtures
@pytest.fixture
async def mock_event_bus():
    """Mock event bus for testing."""
    mock_bus = AsyncMock()
    return mock_bus


@pytest.fixture
async def mock_command_bus():
    """Mock command bus for testing."""
    mock_bus = AsyncMock()
    return mock_bus


@pytest.fixture
async def mock_query_bus():
    """Mock query bus for testing."""
    mock_bus = AsyncMock()
    return mock_bus


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_vin_decode_response(vin: str, service: str = "nhtsa") -> Dict[str, Any]:
        """Create a standard VIN decode response."""
        return {
            "success": True,
            "vin": vin,
            "service": service,
            "attributes": {
                "make": "Honda",
                "model": "Civic",
                "year": 2021,
                "body_type": "Sedan",
                "engine": "1.5L 4-Cylinder",
                "transmission": "CVT",
                "fuel_type": "Gasoline"
            }
        }
    
    @staticmethod
    def create_user_data(telegram_id: int = 123456789) -> Dict[str, Any]:
        """Create user data for testing."""
        return {
            "telegram_id": telegram_id,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User"
        }
    
    @staticmethod
    def create_telegram_message_data(text: str = "/start", user_id: int = 123456789) -> Dict[str, Any]:
        """Create Telegram message data for testing."""
        return {
            "message_id": 1,
            "text": text,
            "from": {
                "id": user_id,
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User"
            },
            "chat": {
                "id": user_id,
                "type": "private"
            },
            "date": datetime.utcnow().timestamp()
        }


@pytest.fixture
def test_data_factory():
    """Test data factory fixture."""
    return TestDataFactory


# Mark all tests as asyncio by default
pytest_asyncio.fixture(scope="function", autouse=True)