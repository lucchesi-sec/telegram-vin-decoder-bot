# VIN Decoder Bot - Development Guidelines & Best Practices

## General Responsibilities
- Guide the development of idiomatic, maintainable, and high-performance Python async code.
- Enforce modular design and separation of concerns through layered architecture.
- Promote type-driven development with comprehensive type hints and mypy validation.
- Ensure robust error handling, caching strategies, and scalable patterns for bot interactions.

## Architecture Patterns
- Apply **layered architecture** by structuring code into handlers, services, clients, and data layers.
- Use **dependency injection** through constructor parameters and protocol/ABC interfaces.
- Implement **repository pattern** for cache abstraction (Upstash).
- Prioritize **protocol-driven development** using Python's Protocol or ABC for interfaces.
- Ensure all service interactions use protocols/interfaces, not concrete implementations.
- Follow **single responsibility principle** - each module/class should have one reason to change.

## Project Structure Guidelines
- Use consistent project layout:
  - `vinbot/`: main package containing all application code
  - `vinbot/handlers/`: Telegram command and message handlers
  - `vinbot/services/`: business logic and VIN processing
  - `vinbot/clients/`: external API clients (CarsXE)
  - `vinbot/cache/`: caching implementations and interfaces
  - `vinbot/models/`: data models and Pydantic schemas
  - `vinbot/utils/`: shared utilities and helpers
  - `vinbot/formatters/`: message formatting logic
  - `tests/`: pytest tests mirroring source structure
  - `debug/`: debugging scripts and tools
- Keep Telegram-specific code isolated in handlers.
- Separate API client logic from business logic.

## Python Async Best Practices
- Use **async/await** consistently throughout the codebase.
- Leverage **asyncio.gather()** for concurrent operations.
- Implement **async context managers** for resource management (`async with`).
- Use **httpx.AsyncClient** with connection pooling for HTTP requests.
- Properly handle **asyncio cancellation** and cleanup in handlers.
- Avoid blocking operations in async functions; use `asyncio.to_thread()` when necessary.
- Implement **graceful shutdown** with proper task cancellation.

## Type Safety and Code Quality
- Use **comprehensive type hints** for all function signatures.
- Leverage **typing module** features: Optional, Union, TypeVar, Protocol, TypedDict.
- Run **mypy** with strict mode (`--strict`) for type validation.
- Use **Pydantic** for data validation and serialization.
- Apply **Black** for consistent code formatting (88 char line length).
- Use **isort** for import organization.
- Enforce **flake8** for style violations.
- Configure **pre-commit hooks** for automatic quality checks.

## Telegram Bot Patterns
- Use **python-telegram-bot's** async API (v20+).
- Implement **conversation handlers** for multi-step interactions.
- Use **filters** for message validation before processing.
- Leverage **callback query handlers** for inline keyboard interactions.
- Implement **error handlers** to catch and log all exceptions.
- Use **job queue** for scheduled tasks and cleanup.
- Apply **rate limiting** per user to prevent abuse.
- Implement **command decorators** for permission checking.

## Caching Strategies
- Define **cache protocol/interface** for abstraction.
- Implement **cache-aside pattern**: check cache, fetch if miss, update cache.
- Use **async Redis operations** with redis-py or aioredis.
- Implement **Upstash REST client** for serverless Redis.
- Set appropriate **TTL values** based on data volatility.
- Handle **cache failures gracefully** - fallback to API.
- Use **cache key namespacing** (e.g., `vin:{vin}`, `user:{id}`).
- Implement **cache warming** for frequently accessed data.
- Consider **cache stampede protection** with locks or probabilistic expiry.

## Error Handling and Resilience
- Create **custom exception hierarchy** for different error types.
- Use **try/except/else/finally** blocks appropriately.
- Implement **exponential backoff** for API retries using tenacity or backoff libraries.
- Add **circuit breaker pattern** for external service calls.
- Log errors with **contextual information** (user_id, vin, timestamp).
- Return **user-friendly error messages** while logging technical details.
- Implement **timeout handling** for all external calls.
- Use **asyncio.TimeoutError** for async timeout management.

## Testing with pytest
- Write **async tests** using pytest-asyncio.
- Use **fixtures** for common test setup (bot, cache, client mocks).
- Implement **parametrized tests** for multiple test cases.
- Mock external dependencies using **unittest.mock** or pytest-mock.
- Use **httpx.AsyncClient** with pytest-httpx for HTTP mocking.
- Test **edge cases**: invalid VINs, API failures, cache misses.
- Achieve **80%+ code coverage** using pytest-cov.
- Separate **unit tests** from integration tests using markers.
- Use **factories** (factory_boy) for test data generation.

## Security Best Practices
- **Never commit secrets** - use environment variables or .env files.
- Validate and **sanitize all user inputs** before processing.
- Implement **rate limiting** per user and globally.
- Use **secrets module** for generating secure tokens.
- Apply **input length limits** to prevent DoS attacks.
- Escape special characters in **Telegram markdown** to prevent injection.
- Implement **user authentication** for sensitive commands.
- Log security events (failed validations, rate limit hits).
- Use **HTTPS only** for external API calls.
- Implement **request signing** if supported by APIs.

## Virtual Environment Management
- Use **venv** or **virtualenv** for environment isolation.
- Pin **exact versions** in requirements.txt for reproducibility.
- Separate **dev dependencies** in requirements-dev.txt.
- Use **pip-tools** for dependency resolution and management.
- Document **Python version** requirements (>=3.8).
- Include **.python-version** file for pyenv users.
- Use **poetry** or **pipenv** for advanced dependency management.
- Always activate venv before development work.

## Fly.io Deployment Considerations
- Implement **/health endpoint** for health checks.
- Use **threading** to run health server alongside bot.
- Handle **SIGTERM gracefully** for zero-downtime deployments.
- Configure **proper memory limits** (1GB for shared-cpu-1x).
- Use **multi-stage Docker builds** to minimize image size.
- Set **non-root user** in Dockerfile for security.
- Implement **readiness checks** before accepting traffic.
- Use **fly secrets** for sensitive environment variables.
- Configure **auto-rollback** on deployment failures.
- Monitor with **fly logs** and implement structured logging.

## Observability and Monitoring
- Use **structured logging** with JSON output for production.
- Include **correlation IDs** in all log entries.
- Log at appropriate levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
- Implement **metrics collection** (request count, latency, errors).
- Use **prometheus_client** for metrics exposition.
- Add **custom metrics** for business events (VINs decoded, cache hits).
- Implement **distributed tracing** with OpenTelemetry if scaling.
- Set up **alerts** for error rates and latency thresholds.

## Performance Optimization
- Use **connection pooling** for Redis and HTTP clients.
- Implement **batch processing** for multiple VIN requests.
- Cache **expensive computations** and API responses.
- Use **asyncio.create_task()** for fire-and-forget operations.
- Profile with **cProfile** and **py-spy** for bottlenecks.
- Optimize **message formatting** to avoid repeated string operations.
- Implement **lazy loading** for optional features.
- Use **__slots__** for frequently instantiated classes.

## Documentation Standards
- Write **docstrings** for all public functions (Google/NumPy style).
- Include **type hints** in function signatures.
- Document **return values** and possible exceptions.
- Maintain **README.md** with setup and usage instructions.
- Create **CLAUDE.md** for AI assistant guidance.
- Document **environment variables** in .env.example.
- Include **API documentation** for service interfaces.
- Write **inline comments** for complex logic only.

## Development Workflow
- Use **Makefile** for common commands (run, test, lint, format).
- Implement **pre-commit hooks** for code quality checks.
- Use **GitHub Actions** for CI/CD pipeline.
- Run **all tests** before committing code.
- Format with **Black** before every commit.
- Sort imports with **isort** automatically.
- Check types with **mypy** in strict mode.
- Lint with **flake8** or **ruff** for style issues.

## Key Python Idioms
1. **"Explicit is better than implicit"** - Clear code over clever code.
2. **"Errors should never pass silently"** - Handle all exceptions explicitly.
3. **"Flat is better than nested"** - Avoid deep nesting, use early returns.
4. **"Simple is better than complex"** - Favor readability over performance until proven necessary.
5. **"Special cases aren't special enough"** - Consistent patterns throughout codebase.

## Redis/Upstash Patterns
- Implement **async cache operations** using aioredis or httpx for Upstash.
- Use **pipeline operations** for multiple Redis commands.
- Implement **cache versioning** for data structure changes.
- Use **Redis data types** appropriately (strings for JSON, sets for unique items).
- Handle **connection failures** with automatic reconnection.
- Implement **cache statistics** (hit rate, miss rate, latency).
- Use **Redis pub/sub** for real-time updates if needed.
- Consider **Redis persistence** settings for data durability.

## Debugging and Troubleshooting
- Create **debug scripts** for testing individual components.
- Use **logging.DEBUG** level for development environments.
- Implement **debug commands** in bot for admin users.
- Use **pdb** or **ipdb** for interactive debugging.
- Create **health check endpoints** exposing system status.
- Log **request/response cycles** for API debugging.
- Use **asyncio debug mode** to detect blocking operations.
- Implement **feature flags** for gradual rollouts.

## Build/Test Commands
- Single test: `python run_tests.py -k test_name`
- Unit tests: `make test-unit` or `python run_tests.py --type unit`
- All tests: `make test` or `python run_tests.py --type all`
- With coverage: `make coverage` or `python run_tests.py --coverage`
- Type check: `python -m mypy src --ignore-missing-imports`
- Lint: `python -m flake8 src --max-line-length=120`
- Format: `black src && isort src`
- Run locally: `make run` or `python -m src.main`

## Code Style
- Line length: 120 chars (flake8 config)
- Type hints: mandatory for all functions
- Async: use `async/await` everywhere, `httpx.AsyncClient`
- Imports: isort sorted, absolute imports preferred
- Naming: `snake_case` functions/vars, `PascalCase` classes
- Error handling: custom exceptions, explicit try/except
- Layered architecture: handlers → services → repositories → clients
- Protocols: use `Protocol` for interfaces, DI via constructors
- Tests: pytest-asyncio async tests always