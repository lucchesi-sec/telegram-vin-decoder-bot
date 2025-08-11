# Domain-Driven Design Transformation Prompt for VIN Decoder Telegram Bot

## The Prompt

```
You are a senior software architect specializing in Domain-Driven Design, clean architecture, and enterprise-grade Python applications. Your task is to completely refactor a Telegram bot repository for VIN (Vehicle Identification Number) decoding into an exemplary, production-ready codebase that demonstrates best practices in software architecture and serves as a reference implementation.

## Current State Analysis

The repository is a Python Telegram bot with the following structure:
- vinbot/ package containing bot.py entry point
- Service classes mixing concerns (vin_service, decoder_service, user_service, message_service)
- Separated callback and command handlers
- Multiple decoder clients (NHTSA, AutoDev)
- User data management with caching
- Debug scripts in debug/ folder
- Basic configuration management
- UI/keyboard components

## Transformation Requirements

### 1. Domain-Driven Design Implementation

Create clear bounded contexts:
- **Vehicle Domain**: Core VIN decoding, vehicle information management
- **User Domain**: User preferences, history, subscription management
- **Messaging Domain**: Telegram interaction, message formatting, UI components
- **Integration Domain**: External API clients, third-party service adapters

For each bounded context:
- Define Ubiquitous Language in a glossary file
- Create context maps showing relationships
- Establish clear boundaries and interfaces

### 2. Layered Architecture Structure

Implement the following directory structure:
```
src/
├── domain/
│   ├── vehicle/
│   │   ├── entities/
│   │   │   ├── vehicle.py (Aggregate Root)
│   │   │   ├── vin.py (Entity)
│   │   │   └── manufacturer.py (Entity)
│   │   ├── value_objects/
│   │   │   ├── vin_number.py
│   │   │   ├── model_year.py
│   │   │   ├── vehicle_attributes.py
│   │   │   └── decode_result.py
│   │   ├── repositories/
│   │   │   └── vehicle_repository.py (Interface)
│   │   ├── services/
│   │   │   └── vin_validation_service.py (Domain Service)
│   │   └── events/
│   │       ├── vehicle_decoded_event.py
│   │       └── decode_failed_event.py
│   ├── user/
│   │   ├── entities/
│   │   │   └── user.py (Aggregate Root)
│   │   ├── value_objects/
│   │   │   ├── telegram_id.py
│   │   │   ├── user_preferences.py
│   │   │   └── subscription_tier.py
│   │   ├── repositories/
│   │   │   └── user_repository.py (Interface)
│   │   └── events/
│   │       └── user_registered_event.py
│   └── shared/
│       ├── domain_event.py
│       ├── entity.py
│       ├── value_object.py
│       └── specification.py
├── application/
│   ├── vehicle/
│   │   ├── commands/
│   │   │   ├── decode_vin_command.py
│   │   │   └── handlers/
│   │   │       └── decode_vin_handler.py
│   │   ├── queries/
│   │   │   ├── get_vehicle_history_query.py
│   │   │   └── handlers/
│   │   │       └── get_vehicle_history_handler.py
│   │   └── services/
│   │       └── vehicle_application_service.py
│   ├── user/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── services/
│   └── shared/
│       ├── command_bus.py
│       ├── query_bus.py
│       └── event_bus.py
├── infrastructure/
│   ├── persistence/
│   │   ├── repositories/
│   │   │   ├── sqlalchemy_vehicle_repository.py
│   │   │   └── redis_cache_repository.py
│   │   ├── models/
│   │   │   └── orm_models.py
│   │   └── unit_of_work.py
│   ├── external_services/
│   │   ├── nhtsa/
│   │   │   ├── nhtsa_client.py
│   │   │   └── nhtsa_adapter.py
│   │   ├── autodev/
│   │   │   ├── autodev_client.py
│   │   │   └── autodev_adapter.py
│   │   └── decoder_factory.py
│   ├── messaging/
│   │   └── telegram/
│   │       ├── bot_client.py
│   │       └── message_adapter.py
│   └── monitoring/
│       ├── logging_config.py
│       ├── metrics_collector.py
│       └── health_check.py
├── presentation/
│   ├── telegram_bot/
│   │   ├── handlers/
│   │   │   ├── command_handlers.py
│   │   │   └── callback_handlers.py
│   │   ├── keyboards/
│   │   │   └── inline_keyboards.py
│   │   ├── formatters/
│   │   │   ├── vehicle_formatter.py
│   │   │   └── error_formatter.py
│   │   └── bot_application.py
│   └── api/ (optional REST API)
│       ├── controllers/
│       └── dto/
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/
│   │   ├── repositories/
│   │   └── external_services/
│   ├── e2e/
│   │   └── telegram_bot/
│   └── fixtures/
│       └── factories/
└── config/
    ├── settings.py
    ├── dependencies.py (DI container)
    └── environments/
```

### 3. Domain Layer Implementation

Create proper domain entities with:
```python
# Example Vehicle Aggregate Root
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from src.domain.shared.entity import AggregateRoot
from src.domain.vehicle.value_objects import VINNumber, ModelYear
from src.domain.vehicle.events import VehicleDecodedEvent

@dataclass
class Vehicle(AggregateRoot):
    vin: VINNumber
    manufacturer: str
    model: str
    model_year: ModelYear
    attributes: Dict[str, Any]
    decode_history: List[DecodeAttempt]
    
    def __post_init__(self):
        super().__init__()
        if self.is_newly_decoded():
            self.add_domain_event(VehicleDecodedEvent(
                vehicle_id=self.id,
                vin=self.vin.value,
                decoded_at=datetime.utcnow()
            ))
    
    def update_attributes(self, new_attributes: Dict[str, Any]) -> None:
        """Business logic for updating vehicle attributes"""
        # Validation and business rules here
        self.attributes.update(new_attributes)
        self.mark_as_modified()
    
    @classmethod
    def decode_from_vin(cls, vin: VINNumber, decoder_result: DecodeResult) -> 'Vehicle':
        """Factory method for creating Vehicle from decode result"""
        # Complex creation logic here
        pass
```

### 4. Application Layer with CQRS

Implement Command/Query Segregation:
```python
# Command Handler Example
from src.application.shared.command_bus import CommandHandler
from src.domain.vehicle.repositories import VehicleRepository
from src.infrastructure.external_services import DecoderFactory

class DecodeVINHandler(CommandHandler[DecodeVINCommand, DecodeResult]):
    def __init__(
        self,
        vehicle_repo: VehicleRepository,
        decoder_factory: DecoderFactory,
        event_bus: EventBus,
        logger: Logger
    ):
        self.vehicle_repo = vehicle_repo
        self.decoder_factory = decoder_factory
        self.event_bus = event_bus
        self.logger = logger
    
    async def handle(self, command: DecodeVINCommand) -> DecodeResult:
        # Check cache first
        existing = await self.vehicle_repo.find_by_vin(command.vin)
        if existing and not command.force_refresh:
            return existing.to_decode_result()
        
        # Select appropriate decoder based on user preferences
        decoder = self.decoder_factory.get_decoder(command.user_preferences)
        
        # Perform decoding with circuit breaker pattern
        try:
            raw_result = await decoder.decode(command.vin)
            vehicle = Vehicle.decode_from_vin(command.vin, raw_result)
            await self.vehicle_repo.save(vehicle)
            
            # Publish domain events
            for event in vehicle.collect_events():
                await self.event_bus.publish(event)
            
            return vehicle.to_decode_result()
        except DecoderException as e:
            self.logger.error(f"Decoding failed for VIN {command.vin}: {e}")
            raise ApplicationException("Unable to decode VIN", cause=e)
```

### 5. Infrastructure Layer with Dependency Injection

Setup dependency injection container:
```python
# config/dependencies.py
from dependency_injector import containers, providers
from src.infrastructure.persistence.repositories import SQLAlchemyVehicleRepository
from src.infrastructure.external_services.nhtsa import NHTSAClient
from src.application.vehicle.services import VehicleApplicationService

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Infrastructure
    database = providers.Singleton(
        Database,
        connection_string=config.database.connection_string
    )
    
    # Repositories
    vehicle_repository = providers.Factory(
        SQLAlchemyVehicleRepository,
        session_factory=database.provided.session_factory
    )
    
    # External Services
    nhtsa_client = providers.Singleton(
        NHTSAClient,
        api_key=config.nhtsa.api_key,
        timeout=config.nhtsa.timeout
    )
    
    # Application Services
    vehicle_service = providers.Factory(
        VehicleApplicationService,
        repository=vehicle_repository,
        decoder=nhtsa_client,
        cache=providers.Singleton(RedisCache)
    )
    
    # Command/Query Handlers
    decode_vin_handler = providers.Factory(
        DecodeVINHandler,
        vehicle_repo=vehicle_repository,
        decoder_factory=providers.Factory(DecoderFactory),
        event_bus=providers.Singleton(EventBus)
    )
```

### 6. Testing Strategy

Implement comprehensive testing:
```python
# tests/unit/domain/vehicle/test_vehicle.py
import pytest
from src.domain.vehicle.entities import Vehicle
from src.domain.vehicle.value_objects import VINNumber

class TestVehicle:
    def test_vehicle_creation_emits_decoded_event(self):
        vin = VINNumber("1HGBH41JXMN109186")
        vehicle = Vehicle(vin=vin, manufacturer="Honda", model="Civic", model_year=2023)
        
        events = vehicle.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], VehicleDecodedEvent)
    
    def test_vehicle_invariants(self):
        """Test that domain invariants are maintained"""
        # Test business rules
        pass

# tests/integration/test_decoder_integration.py
@pytest.mark.integration
class TestDecoderIntegration:
    async def test_nhtsa_decoder_with_real_api(self):
        """Test actual NHTSA API integration"""
        pass

# tests/e2e/test_telegram_flow.py
@pytest.mark.e2e
class TestTelegramBotFlow:
    async def test_complete_vin_decode_flow(self, telegram_bot_fixture):
        """Test complete user journey from message to response"""
        pass
```

### 7. Error Handling and Resilience

Implement comprehensive error handling:
```python
# src/infrastructure/resilience/circuit_breaker.py
from typing import Optional, Callable
import asyncio
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"
    
    async def call(self, func: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

# Use in decoder
class ResilientDecoder:
    def __init__(self, decoder: Decoder):
        self.decoder = decoder
        self.circuit_breaker = CircuitBreaker()
        self.retry_policy = RetryPolicy(max_attempts=3, backoff_factor=2)
    
    async def decode(self, vin: str) -> DecodeResult:
        return await self.retry_policy.execute(
            lambda: self.circuit_breaker.call(self.decoder.decode, vin)
        )
```

### 8. Monitoring and Observability

Add comprehensive monitoring:
```python
# src/infrastructure/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import structlog

# Metrics
decode_requests = Counter('vin_decode_requests_total', 'Total VIN decode requests')
decode_duration = Histogram('vin_decode_duration_seconds', 'VIN decode duration')
active_users = Gauge('telegram_active_users', 'Number of active Telegram users')

# Structured Logging
logger = structlog.get_logger()

class MonitoredVehicleService:
    @decode_duration.time()
    async def decode_vin(self, vin: str) -> DecodeResult:
        decode_requests.inc()
        logger.info("vin_decode_started", vin=vin, timestamp=datetime.utcnow())
        
        try:
            result = await self._decode_internal(vin)
            logger.info("vin_decode_completed", vin=vin, success=True)
            return result
        except Exception as e:
            logger.error("vin_decode_failed", vin=vin, error=str(e))
            raise
```

### 9. CI/CD Pipeline

Create GitHub Actions workflow:
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run linters
        run: |
          ruff check src tests
          mypy src --strict
          black --check src tests
      
      - name: Run tests with coverage
        run: |
          pytest tests/unit --cov=src --cov-report=xml
          pytest tests/integration --markers=integration
      
      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      
      - name: Build Docker image
        run: |
          docker build -t vin-bot:${{ github.sha }} .
      
      - name: Run security scan
        run: |
          trivy image vin-bot:${{ github.sha }}

  deploy:
    needs: quality
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deployment steps here
```

### 10. Documentation and ADRs

Create Architecture Decision Records:
```markdown
# docs/adr/001-use-domain-driven-design.md
# ADR-001: Use Domain-Driven Design

## Status
Accepted

## Context
The VIN decoder bot has grown complex with mixed concerns and unclear boundaries.

## Decision
We will implement Domain-Driven Design with clear bounded contexts.

## Consequences
- Pros: Clear separation of concerns, better maintainability, easier testing
- Cons: Initial complexity, learning curve for team

# docs/adr/002-implement-cqrs.md
# ADR-002: Implement CQRS Pattern

## Status
Accepted

## Context
Read and write operations have different scaling requirements.

## Decision
Implement CQRS to separate command and query responsibilities.

## Consequences
- Pros: Optimized read/write paths, better scalability
- Cons: Additional complexity, eventual consistency considerations
```

### 11. Event-Driven Architecture

Implement domain events:
```python
# src/domain/shared/domain_event.py
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
import uuid

@dataclass
class DomainEvent(ABC):
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    aggregate_id: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# src/infrastructure/messaging/event_store.py
class EventStore:
    async def append(self, stream_name: str, events: List[DomainEvent]) -> None:
        """Append events to stream"""
        pass
    
    async def read_stream(self, stream_name: str, from_version: int = 0) -> List[DomainEvent]:
        """Read events from stream"""
        pass

# Event Handlers
class UpdateUserStatsOnVehicleDecoded:
    async def handle(self, event: VehicleDecodedEvent) -> None:
        user = await self.user_repo.find_by_id(event.user_id)
        user.increment_decode_count()
        await self.user_repo.save(user)
```

### 12. Configuration Management

Implement proper settings:
```python
# src/config/settings.py
from pydantic import BaseSettings, Field, SecretStr
from typing import Optional

class DatabaseSettings(BaseSettings):
    connection_string: SecretStr = Field(..., env="DATABASE_URL")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    echo: bool = Field(default=False, env="DB_ECHO")

class TelegramSettings(BaseSettings):
    bot_token: SecretStr = Field(..., env="TELEGRAM_BOT_TOKEN")
    webhook_url: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_URL")
    max_connections: int = Field(default=40, env="TELEGRAM_MAX_CONNECTIONS")

class DecoderSettings(BaseSettings):
    nhtsa_api_key: Optional[SecretStr] = Field(None, env="NHTSA_API_KEY")
    autodev_api_key: Optional[SecretStr] = Field(None, env="AUTODEV_API_KEY")
    cache_ttl: int = Field(default=3600, env="DECODER_CACHE_TTL")
    timeout: int = Field(default=30, env="DECODER_TIMEOUT")

class Settings(BaseSettings):
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    database: DatabaseSettings = DatabaseSettings()
    telegram: TelegramSettings = TelegramSettings()
    decoder: DecoderSettings = DecoderSettings()
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
```

### 13. Performance Optimization

Add caching and optimization:
```python
# src/infrastructure/caching/cache_decorators.py
from functools import wraps
import hashlib
import json

def cache_result(ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hashlib.md5(
                json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True).encode()
            ).hexdigest()}"
            
            # Try to get from cache
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            # Execute and cache
            result = await func(self, *args, **kwargs)
            await self.cache.set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator

# Use in repository
class CachedVehicleRepository:
    @cache_result(ttl=3600)
    async def find_by_vin(self, vin: str) -> Optional[Vehicle]:
        return await self._repository.find_by_vin(vin)
```

### 14. Security Implementation

Add security layers:
```python
# src/infrastructure/security/rate_limiter.py
from typing import Dict
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = {}
    
    async def check_rate_limit(self, user_id: str) -> bool:
        now = datetime.utcnow()
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < timedelta(seconds=self.window_seconds)
        ]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True

# Input validation
from pydantic import BaseModel, validator

class VINInput(BaseModel):
    vin: str
    
    @validator('vin')
    def validate_vin_format(cls, v):
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', v):
            raise ValueError('Invalid VIN format')
        return v.upper()
```

### 15. Database Migrations

Setup Alembic for migrations:
```python
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from src.infrastructure.persistence.models import Base

config = context.config

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        
        with context.begin_transaction():
            context.run_migrations()
```

## Execution Instructions

1. **Phase 1 - Analysis and Planning** (Day 1-2)
   - Analyze existing codebase and identify all domain concepts
   - Create bounded context maps and domain models
   - Write ADRs for major architectural decisions
   - Create detailed migration plan

2. **Phase 2 - Domain Layer** (Day 3-5)
   - Implement all value objects with validation
   - Create domain entities and aggregates
   - Define repository interfaces
   - Implement domain services and events

3. **Phase 3 - Application Layer** (Day 6-7)
   - Implement CQRS command and query handlers
   - Create application services
   - Setup event bus and command bus
   - Implement use case orchestration

4. **Phase 4 - Infrastructure Layer** (Day 8-10)
   - Implement repository concrete classes
   - Setup external service adapters
   - Configure dependency injection
   - Implement caching and resilience patterns

5. **Phase 5 - Presentation Layer** (Day 11-12)
   - Refactor Telegram bot handlers
   - Implement proper DTOs and formatters
   - Add input validation and sanitization
   - Setup API documentation

6. **Phase 6 - Testing** (Day 13-14)
   - Write comprehensive unit tests (>90% coverage)
   - Create integration tests for external services
   - Implement E2E tests for critical paths
   - Setup test fixtures and factories

7. **Phase 7 - DevOps and Monitoring** (Day 15)
   - Setup CI/CD pipelines
   - Configure monitoring and alerting
   - Implement health checks
   - Create deployment scripts

8. **Phase 8 - Documentation** (Day 16)
   - Write comprehensive README
   - Create API documentation
   - Document architectural decisions
   - Create onboarding guide

## Success Criteria

- Zero mixed concerns - each module has single responsibility
- 90%+ test coverage with all types of tests
- All external dependencies behind adapters
- Domain logic completely isolated from infrastructure
- Comprehensive error handling and logging
- Performance metrics and monitoring in place
- Clear documentation and onboarding materials
- Passing all quality gates (linting, type checking, security scans)
- Deployable via single command
- Rollback capability
- Feature flags for gradual rollout
- A/B testing capability for decoder selection

## Deliverables

1. Fully refactored codebase following DDD principles
2. Complete test suite (unit, integration, E2E)
3. CI/CD pipeline configuration
4. Deployment scripts and infrastructure as code
5. Comprehensive documentation including:
   - Architecture overview
   - API documentation
   - ADRs for all major decisions
   - Developer onboarding guide
   - Operations runbook
6. Monitoring dashboards and alerts
7. Performance benchmarks
8. Security audit report

The final codebase should serve as a reference implementation that demonstrates enterprise-grade Python development with Domain-Driven Design, suitable for use as a template for future projects.
```

## Implementation Notes

### Key Techniques Used
- **Role-playing**: Positioned the agent as a senior software architect with specific expertise
- **Structured requirements**: Clear, numbered sections with specific deliverables
- **Code examples**: Provided concrete implementation examples to guide the transformation
- **Phased approach**: Breaking down the work into manageable phases with timelines
- **Success criteria**: Clear, measurable outcomes to validate completion
- **Context preservation**: Maintained awareness of the existing codebase structure

### Why These Choices Were Made
- **DDD focus**: Addresses the core architectural issues in the current codebase
- **Comprehensive scope**: Covers all aspects from domain modeling to deployment
- **Practical examples**: Shows exactly how to implement concepts, not just theory
- **Enterprise patterns**: Includes production-ready patterns like circuit breakers, event sourcing, CQRS
- **Testing emphasis**: Ensures quality through comprehensive testing strategy
- **DevOps integration**: Makes the solution deployable and maintainable

### Expected Outcomes
- Complete architectural transformation following DDD principles
- Clear separation of concerns across all layers
- Production-ready codebase with enterprise patterns
- Comprehensive testing and documentation
- Zero technical debt starting point
- Reference implementation quality suitable for showcasing

The prompt provides specific, actionable guidance while maintaining flexibility for the agent to make appropriate implementation decisions based on the actual codebase details.