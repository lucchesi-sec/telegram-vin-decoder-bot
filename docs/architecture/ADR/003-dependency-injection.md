# ADR-003: Use Dependency Injection Container

## Status
Accepted

## Context
With Clean Architecture (ADR-002), we have many interfaces and implementations that need to be wired together. Manual dependency management becomes complex as the application grows, leading to boilerplate code and difficulty in testing with different configurations.

### Problem Statement
- Manual dependency wiring is error-prone
- Difficult to manage component lifecycles
- Hard to swap implementations for testing
- Configuration management is scattered
- Circular dependencies are hard to detect

### Requirements
- Automatic dependency resolution
- Support for different component lifecycles
- Easy configuration management
- Support for testing with mocks
- Clear dependency graph

## Decision
We will use the `dependency-injector` library as our IoC (Inversion of Control) container.

### Key Features Utilized
- **Providers**: Factory, Singleton, Resource
- **Wiring**: Automatic injection into modules
- **Configuration**: Centralized configuration management
- **Overriding**: Easy mocking for tests
- **Type hints**: Full type safety support

### Container Structure
```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Settings
    settings = providers.Singleton(Settings)
    
    # External Services
    nhtsa_client = providers.Singleton(
        NHTSAClient,
        timeout=providers.Factory(lambda s: s.decoder.timeout, settings)
    )
    
    # Repositories
    vehicle_repository = providers.Singleton(
        InMemoryVehicleRepository
    )
    
    # Application Services
    decode_vin_handler = providers.Factory(
        DecodeVINHandler,
        vehicle_repo=vehicle_repository,
        decoder_factory=decoder_factory,
        event_bus=event_bus
    )
```

## Consequences

### Positive
- **Automatic wiring**: Dependencies resolved automatically
- **Lifecycle management**: Singleton, factory, resource patterns
- **Testing support**: Easy to override for tests
- **Configuration**: Centralized and type-safe
- **Documentation**: Container documents all dependencies
- **Error detection**: Circular dependencies caught early

### Negative
- **Learning curve**: Team needs to learn DI concepts
- **Runtime resolution**: Errors might appear at runtime
- **Magic**: Less explicit than manual wiring
- **Debugging**: Stack traces through container

### Neutral
- **Performance**: Minimal overhead after initial wiring
- **Library dependency**: Tied to dependency-injector

## Implementation

### Provider Types

#### Singleton Provider
```python
# Shared instance across application
database_connection = providers.Singleton(
    DatabaseConnection,
    connection_string=config.database.url
)
```

#### Factory Provider
```python
# New instance each time
command_handler = providers.Factory(
    CommandHandler,
    repository=vehicle_repository
)
```

#### Resource Provider
```python
# Managed lifecycle (context manager)
@providers.Resource
def database_session():
    session = create_session()
    yield session
    session.close()
```

### Configuration Management
```python
class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Load from environment
    config.from_env("APP_CONFIG", required=True)
    
    # Load from file
    config.from_yaml("config.yaml")
    
    # Use in providers
    api_client = providers.Singleton(
        APIClient,
        api_key=config.api.key,
        timeout=config.api.timeout
    )
```

### Testing with Overrides
```python
@pytest.fixture
def container():
    container = Container()
    
    # Override with mocks
    container.vehicle_repository.override(
        providers.Singleton(MockVehicleRepository)
    )
    
    yield container
    
    container.reset_override()

def test_decode_vin(container):
    handler = container.decode_vin_handler()
    result = await handler.handle(command)
    assert result.vin == command.vin
```

### Wiring to Modules
```python
# main.py
container = Container()
container.wire(modules=[
    "src.presentation.telegram_bot.handlers",
    "src.application.services"
])

# In handler module - automatic injection
from dependency_injector.wiring import inject, Provide

class VINCommandHandler:
    @inject
    def __init__(
        self,
        vehicle_service: VehicleApplicationService = Provide[Container.vehicle_application_service]
    ):
        self._vehicle_service = vehicle_service
```

## Alternatives Considered

### 1. Manual Dependency Injection
- **Pros**: Explicit, no magic, no library needed
- **Cons**: Boilerplate, error-prone, hard to maintain
- **Reason rejected**: Too much manual wiring code

### 2. Python's Built-in DI (functools)
- **Pros**: No external dependency, simple
- **Cons**: Limited features, no lifecycle management
- **Reason rejected**: Insufficient for complex needs

### 3. Other DI Libraries
#### Injector
- **Pros**: Simple API, good documentation
- **Cons**: Less features, smaller community
- **Reason rejected**: dependency-injector more feature-rich

#### Pinject
- **Pros**: Google's solution, implicit binding
- **Cons**: Too much magic, less maintained
- **Reason rejected**: Too implicit, maintenance concerns

### 4. Service Locator Pattern
- **Pros**: Simple to understand
- **Cons**: Anti-pattern, hidden dependencies
- **Reason rejected**: Violates explicit dependencies principle

## Migration Strategy

### Phase 1: Container Setup
1. Install dependency-injector
2. Create Container class
3. Define providers for existing components

### Phase 2: Wiring
1. Wire container to existing modules
2. Add @inject decorators
3. Update imports to use Provide

### Phase 3: Testing
1. Create test containers
2. Add override fixtures
3. Update tests to use DI

## Best Practices

### DO
- Use Singleton for shared state
- Use Factory for stateless services
- Use Resource for managed lifecycles
- Override dependencies in tests
- Keep container configuration simple

### DON'T
- Don't use container as service locator
- Don't create circular dependencies
- Don't override in production code
- Don't use container directly in domain

## Validation Checklist
- [ ] All dependencies defined in container
- [ ] No circular dependencies
- [ ] Tests use overrides properly
- [ ] Configuration is centralized
- [ ] Wiring is explicit in main
- [ ] Type hints work correctly

## References
- [dependency-injector Documentation](https://python-dependency-injector.ets-labs.org/)
- [Dependency Injection Principles](https://www.martinfowler.com/articles/injection.html)
- [IoC Container Pattern](https://martinfowler.com/articles/injection.html#InversionOfControl)
- [SOLID Principles](https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)

## Related ADRs
- ADR-002: Clean Architecture (requires DI)
- ADR-004: Configuration Management (uses config provider)
- ADR-006: Testing Strategy (uses override feature)

---
*Date: 2025-01-11*  
*Authors: Engineering Team*  
*Reviewers: Architecture Board*