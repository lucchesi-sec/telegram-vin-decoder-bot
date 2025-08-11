# ADR-002: Implement Clean Architecture

## Status
Accepted

## Context
Following our adoption of Domain-Driven Design (ADR-001), we need a concrete architectural pattern to enforce proper separation of concerns and dependency management. The application needs to remain flexible for future changes in frameworks, databases, and external services.

### Problem Statement
- Framework coupling makes testing difficult
- External service changes ripple through the codebase
- Business logic gets contaminated with technical details
- Difficult to swap implementations (e.g., switching databases)

### Requirements
- Business logic independent of frameworks
- Testable without external dependencies
- Easy to replace technical implementations
- Clear dependency rules

## Decision
We will implement Clean Architecture (also known as Hexagonal Architecture or Ports and Adapters) with strict dependency rules.

### Layer Structure
```
┌─────────────────────────────────────┐
│     Presentation (Controllers)      │ ← Depends on Application & Domain
├─────────────────────────────────────┤
│      Application (Use Cases)        │ ← Depends on Domain only
├─────────────────────────────────────┤
│       Domain (Entities, VOs)        │ ← No dependencies
├─────────────────────────────────────┤
│   Infrastructure (Implementations)   │ ← Depends on Application & Domain
└─────────────────────────────────────┘
```

### Dependency Rule
Dependencies point inward. Inner layers know nothing about outer layers.

### Layer Responsibilities

#### Domain Layer (Core)
- Entities and Value Objects
- Domain Services
- Repository Interfaces (ports)
- Domain Events
- Pure business logic

#### Application Layer
- Use Cases (Command/Query Handlers)
- Application Services
- DTOs for data transfer
- Orchestration logic
- Transaction boundaries

#### Infrastructure Layer
- Repository Implementations
- External Service Clients
- Message Queue Implementations
- Framework-specific code
- Database access

#### Presentation Layer
- Controllers/Handlers
- View Models
- User Interface logic
- Request/Response handling

## Consequences

### Positive
- **Framework Independence**: Can change frameworks without touching business logic
- **Testability**: Each layer can be tested in isolation
- **Flexibility**: Easy to swap implementations
- **Clear boundaries**: Obvious where code belongs
- **Parallel development**: Teams can work on different layers
- **Technology agnostic**: Core business logic is pure Python

### Negative
- **More code**: Interfaces, DTOs, and mappings add boilerplate
- **Indirection**: More layers to navigate
- **Learning curve**: Team needs to understand the architecture
- **Initial setup**: More structure to establish upfront

### Neutral
- **Performance**: Marginal overhead from layer boundaries
- **Debugging**: More layers to trace through

## Implementation

### Example: Repository Pattern
```python
# Domain Layer - Interface (Port)
class VehicleRepository(ABC):
    @abstractmethod
    async def save(self, vehicle: Vehicle) -> None:
        pass
    
    @abstractmethod
    async def find_by_vin(self, vin: VIN) -> Optional[Vehicle]:
        pass

# Infrastructure Layer - Implementation (Adapter)
class PostgreSQLVehicleRepository(VehicleRepository):
    def __init__(self, connection_pool):
        self._pool = connection_pool
    
    async def save(self, vehicle: Vehicle) -> None:
        # PostgreSQL-specific implementation
        pass
    
    async def find_by_vin(self, vin: VIN) -> Optional[Vehicle]:
        # PostgreSQL-specific implementation
        pass
```

### Example: Use Case
```python
# Application Layer - Use Case
class DecodeVINHandler:
    def __init__(
        self,
        vehicle_repo: VehicleRepository,  # Interface, not implementation
        decoder_factory: DecoderFactory,
        event_bus: EventBus
    ):
        self._vehicle_repo = vehicle_repo
        self._decoder_factory = decoder_factory
        self._event_bus = event_bus
    
    async def handle(self, command: DecodeVINCommand) -> Vehicle:
        # Check if already decoded
        existing = await self._vehicle_repo.find_by_vin(command.vin)
        if existing and not command.force_refresh:
            return existing
        
        # Decode using appropriate service
        decoder = self._decoder_factory.get_decoder(command.preference)
        vehicle_info = await decoder.decode(command.vin)
        
        # Create or update vehicle
        vehicle = Vehicle.create(command.vin, vehicle_info)
        await self._vehicle_repo.save(vehicle)
        
        # Publish event
        await self._event_bus.publish(
            VehicleDecoded(vehicle.id, vehicle.vin, vehicle.decoded_at)
        )
        
        return vehicle
```

### Dependency Injection Setup
```python
# Infrastructure Layer - DI Container
class Container(containers.DeclarativeContainer):
    # Infrastructure implementations
    vehicle_repository = providers.Singleton(
        PostgreSQLVehicleRepository,
        connection_pool=providers.Resource(create_connection_pool)
    )
    
    # Application layer with injected dependencies
    decode_vin_handler = providers.Factory(
        DecodeVINHandler,
        vehicle_repo=vehicle_repository,  # Injects implementation
        decoder_factory=decoder_factory,
        event_bus=event_bus
    )
```

## Alternatives Considered

### 1. Layered Architecture (Traditional)
- **Pros**: Familiar, simpler structure
- **Cons**: Layers depend on layers below, not just interfaces
- **Reason rejected**: Tight coupling between layers

### 2. Microservices Architecture
- **Pros**: Ultimate separation, independent deployment
- **Cons**: Operational complexity, network overhead
- **Reason rejected**: Overkill for current scale

### 3. Modular Monolith
- **Pros**: Module independence, simpler than microservices
- **Cons**: Less clear boundaries than Clean Architecture
- **Reason rejected**: Clean Architecture provides clearer rules

### 4. MVC/MVP/MVVM
- **Pros**: Well-known patterns, good for UI apps
- **Cons**: Not ideal for domain-rich applications
- **Reason rejected**: Insufficient for complex business logic

## Migration Strategy

### Phase 1: Structure Setup
1. Create layer directories
2. Define interfaces in domain layer
3. Move existing code to appropriate layers

### Phase 2: Dependency Inversion
1. Extract interfaces from implementations
2. Update imports to use interfaces
3. Configure dependency injection

### Phase 3: Testing
1. Add unit tests for each layer
2. Add integration tests for layer boundaries
3. Add end-to-end tests for full flow

## Validation Checklist
- [ ] Domain layer has no external dependencies
- [ ] Application layer depends only on domain
- [ ] Infrastructure depends on application interfaces
- [ ] No framework code in domain or application layers
- [ ] All external dependencies are behind interfaces
- [ ] Tests can run without external services

## References
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Ports and Adapters Pattern](https://www.dossier-andreas.net/software_architecture/ports_and_adapters.html)
- [Clean Architecture in Python](https://www.cosmicpython.com/)

## Related ADRs
- ADR-001: Domain-Driven Design (defines domain model)
- ADR-003: Dependency Injection Container (implements dependency inversion)
- ADR-005: Repository Pattern (example of ports and adapters)

---
*Date: 2025-01-11*  
*Authors: Engineering Team*  
*Reviewers: Architecture Board*