"""Test helpers and utilities."""

import asyncio
import json
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta
import httpx
from telegram import Update, Bot, Message, User, Chat
from telegram.ext import ContextTypes

T = TypeVar('T')


class AsyncContextManagerMock:
    """Mock for async context managers."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
        self.aenter_called = False
        self.aexit_called = False
    
    async def __aenter__(self):
        self.aenter_called = True
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.aexit_called = True
        return False


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        raise_on_status: bool = False
    ):
        self.status_code = status_code
        self._json_data = json_data or {}
        self._text = text or json.dumps(self._json_data)
        self.headers = headers or {}
        self._raise_on_status = raise_on_status
    
    def json(self) -> Dict[str, Any]:
        """Return JSON data."""
        return self._json_data
    
    async def json_async(self) -> Dict[str, Any]:
        """Return JSON data asynchronously."""
        return self._json_data
    
    @property
    def text(self) -> str:
        """Return text content."""
        return self._text
    
    async def text_async(self) -> str:
        """Return text content asynchronously."""
        return self._text
    
    def raise_for_status(self):
        """Raise exception if status is error."""
        if self._raise_on_status or self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=None,
                response=self
            )


class AsyncIteratorMock:
    """Mock for async iterators."""
    
    def __init__(self, items: List[Any]):
        self.items = items
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


def create_mock_telegram_user(
    user_id: int = 123456789,
    username: str = "testuser",
    first_name: str = "Test",
    last_name: str = "User",
    is_bot: bool = False
) -> Mock:
    """Create a mock Telegram User."""
    user = Mock(spec=User)
    user.id = user_id
    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.is_bot = is_bot
    user.language_code = "en"
    return user


def create_mock_telegram_chat(
    chat_id: int = 123456789,
    chat_type: str = "private",
    title: Optional[str] = None,
    username: Optional[str] = None
) -> Mock:
    """Create a mock Telegram Chat."""
    chat = Mock(spec=Chat)
    chat.id = chat_id
    chat.type = chat_type
    chat.title = title
    chat.username = username
    return chat


def create_mock_telegram_message(
    message_id: int = 1,
    text: str = "/start",
    user: Optional[Mock] = None,
    chat: Optional[Mock] = None,
    date: Optional[datetime] = None
) -> Mock:
    """Create a mock Telegram Message."""
    message = Mock(spec=Message)
    message.message_id = message_id
    message.text = text
    message.from_user = user or create_mock_telegram_user()
    message.chat = chat or create_mock_telegram_chat()
    message.date = date or datetime.utcnow()
    message.reply_text = AsyncMock(return_value=message)
    message.reply_html = AsyncMock(return_value=message)
    message.reply_markdown = AsyncMock(return_value=message)
    message.edit_text = AsyncMock(return_value=message)
    message.delete = AsyncMock()
    return message


def create_mock_telegram_update(
    update_id: int = 1,
    message: Optional[Mock] = None,
    callback_query: Optional[Mock] = None,
    inline_query: Optional[Mock] = None
) -> Mock:
    """Create a mock Telegram Update."""
    update = Mock(spec=Update)
    update.update_id = update_id
    update.message = message
    update.callback_query = callback_query
    update.inline_query = inline_query
    update.effective_user = (message and message.from_user) or (callback_query and callback_query.from_user)
    update.effective_chat = message and message.chat
    update.effective_message = message
    return update


def create_mock_telegram_context(
    bot: Optional[Mock] = None,
    user_data: Optional[Dict[str, Any]] = None,
    chat_data: Optional[Dict[str, Any]] = None,
    bot_data: Optional[Dict[str, Any]] = None
) -> Mock:
    """Create a mock Telegram Context."""
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = bot or Mock(spec=Bot)
    context.user_data = user_data or {}
    context.chat_data = chat_data or {}
    context.bot_data = bot_data or {}
    context.error = None
    return context


class AsyncTestCase:
    """Base class for async test cases."""
    
    @staticmethod
    def run_async(coro):
        """Run an async coroutine in a test."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    
    @staticmethod
    async def wait_for(condition: Callable[[], bool], timeout: float = 1.0):
        """Wait for a condition to be true."""
        start_time = asyncio.get_event_loop().time()
        while not condition():
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Condition not met within {timeout} seconds")
            await asyncio.sleep(0.01)
    
    @staticmethod
    async def assert_async_called_once_with(mock: AsyncMock, *args, **kwargs):
        """Assert an async mock was called once with specific arguments."""
        mock.assert_called_once_with(*args, **kwargs)
    
    @staticmethod
    async def assert_async_called_with(mock: AsyncMock, *args, **kwargs):
        """Assert an async mock was called with specific arguments."""
        mock.assert_called_with(*args, **kwargs)


@contextmanager
def mock_environment_variables(**variables):
    """Context manager to temporarily set environment variables."""
    with patch.dict('os.environ', variables):
        yield


@asynccontextmanager
async def mock_httpx_client(responses: List[MockResponse]):
    """Context manager to mock httpx async client."""
    response_iter = iter(responses)
    
    async def mock_get(*args, **kwargs):
        return next(response_iter)
    
    async def mock_post(*args, **kwargs):
        return next(response_iter)
    
    mock_client = AsyncMock()
    mock_client.get = mock_get
    mock_client.post = mock_post
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        yield mock_client


def assert_domain_event_raised(
    entity: Any,
    event_type: Type[T],
    predicate: Optional[Callable[[T], bool]] = None
) -> T:
    """Assert that a domain event was raised."""
    events = getattr(entity, '_events', [])
    matching_events = [e for e in events if isinstance(e, event_type)]
    
    if not matching_events:
        raise AssertionError(f"No event of type {event_type.__name__} was raised")
    
    if predicate:
        matching_events = [e for e in matching_events if predicate(e)]
        if not matching_events:
            raise AssertionError(f"No event of type {event_type.__name__} matching predicate was raised")
    
    return matching_events[0]


def create_mock_redis_client():
    """Create a mock Redis client."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=1)
    mock_redis.exists = AsyncMock(return_value=0)
    mock_redis.expire = AsyncMock(return_value=True)
    mock_redis.ttl = AsyncMock(return_value=-1)
    mock_redis.keys = AsyncMock(return_value=[])
    mock_redis.mget = AsyncMock(return_value=[])
    mock_redis.mset = AsyncMock(return_value=True)
    return mock_redis


def create_mock_cache_repository():
    """Create a mock cache repository."""
    mock_cache = AsyncMock()
    mock_cache.get = AsyncMock(return_value=None)
    mock_cache.set = AsyncMock(return_value=True)
    mock_cache.delete = AsyncMock(return_value=True)
    mock_cache.exists = AsyncMock(return_value=False)
    mock_cache.clear = AsyncMock(return_value=True)
    return mock_cache


class TimeTracker:
    """Track execution time for performance tests."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.utcnow()
        self.duration = (self.end_time - self.start_time).total_seconds()
    
    def assert_duration_less_than(self, seconds: float):
        """Assert the tracked duration is less than specified seconds."""
        if self.duration is None:
            raise RuntimeError("Timer not used in context manager")
        assert self.duration < seconds, f"Operation took {self.duration}s, expected less than {seconds}s"


def create_test_database_url(db_name: str = "test_db") -> str:
    """Create a test database URL."""
    return f"sqlite:///:memory:"


async def cleanup_async_resources(*resources):
    """Clean up async resources."""
    for resource in resources:
        if hasattr(resource, 'close'):
            if asyncio.iscoroutinefunction(resource.close):
                await resource.close()
            else:
                resource.close()
        elif hasattr(resource, 'cleanup'):
            if asyncio.iscoroutinefunction(resource.cleanup):
                await resource.cleanup()
            else:
                resource.cleanup()