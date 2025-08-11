# C4 Model Diagrams - VIN Decoder Bot

## Overview
This document contains detailed C4 model diagrams for the VIN Decoder Bot system, following Simon Brown's C4 model methodology. The diagrams are provided in multiple formats: Mermaid (for GitHub rendering), PlantUML (for detailed diagrams), and Structurizr DSL (for interactive exploration).

## Level 1: System Context

### Purpose
Shows the VIN Decoder Bot system in context with its users and external systems.

### Mermaid Diagram
```mermaid
graph TB
    subgraph "System Context"
        User[fa:fa-user Telegram User<br/>Person]
        Admin[fa:fa-user-shield System Admin<br/>Person]
    end
    
    subgraph "VIN Decoder System"
        Bot[fa:fa-robot VIN Decoder Bot<br/>Software System]
    end
    
    subgraph "External Systems"
        Telegram[fa:fa-paper-plane Telegram Platform<br/>External System]
        NHTSA[fa:fa-car NHTSA API<br/>External System]
        AutoDev[fa:fa-car-side Auto.dev API<br/>External System]
        Monitoring[fa:fa-chart-line Monitoring System<br/>External System]
    end
    
    User -->|Sends VIN queries<br/>Receives vehicle info| Bot
    Admin -->|Manages configuration<br/>Monitors system| Bot
    Bot -->|Sends/receives messages| Telegram
    Bot -->|Queries VIN data| NHTSA
    Bot -->|Queries premium data| AutoDev
    Bot -->|Sends metrics & logs| Monitoring
    
    style User fill:#08427b,color:#fff
    style Admin fill:#08427b,color:#fff
    style Bot fill:#1168bd,color:#fff
    style Telegram fill:#999999,color:#fff
    style NHTSA fill:#999999,color:#fff
    style AutoDev fill:#999999,color:#fff
    style Monitoring fill:#999999,color:#fff
```

### PlantUML Diagram
```plantuml
@startuml C4_Context
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title System Context - VIN Decoder Bot

Person(user, "Telegram User", "Vehicle owner or enthusiast querying VIN information")
Person(admin, "System Admin", "Manages bot configuration and monitors health")

System(vinbot, "VIN Decoder Bot", "Provides vehicle information through VIN decoding via Telegram interface")

System_Ext(telegram, "Telegram Platform", "Messaging platform for bot interaction")
System_Ext(nhtsa, "NHTSA API", "Free government VIN decoder service")
System_Ext(autodev, "Auto.dev API", "Premium vehicle data provider")
System_Ext(monitoring, "Monitoring System", "Logs, metrics, and alerting")

Rel(user, vinbot, "Sends VIN queries", "Telegram Messages")
Rel(vinbot, user, "Returns vehicle info", "Telegram Messages")
Rel(admin, vinbot, "Manages", "SSH/Config")
Rel(vinbot, telegram, "Uses", "Bot API/HTTPS")
Rel(vinbot, nhtsa, "Queries", "REST/HTTPS")
Rel(vinbot, autodev, "Queries", "REST/HTTPS")
Rel(vinbot, monitoring, "Sends", "Logs/Metrics")

@enduml
```

### Key Relationships
- **Users → Bot**: Natural language VIN queries via Telegram
- **Bot → External APIs**: RESTful API calls for VIN decoding
- **Bot → Telegram**: Bot API for message handling
- **Bot → Monitoring**: Observability data streaming

## Level 2: Container Diagram

### Purpose
Shows the high-level technology choices and how containers communicate.

### Mermaid Diagram
```mermaid
graph TB
    subgraph "Telegram Platform"
        TG[fa:fa-paper-plane Telegram API<br/>External Service]
    end
    
    subgraph "VIN Decoder System Boundary"
        subgraph "Application Container"
            Bot[fa:fa-robot Bot Application<br/>Python/Async<br/>Core business logic]
            DI[fa:fa-plug DI Container<br/>dependency-injector<br/>Component wiring]
        end
        
        subgraph "Storage Containers"
            Cache[fa:fa-database In-Memory Cache<br/>Python Dict<br/>Session storage]
            Future_DB[fa:fa-database PostgreSQL<br/>Future<br/>Persistent storage]
            Future_Redis[fa:fa-database Redis<br/>Future<br/>Distributed cache]
        end
    end
    
    subgraph "External Services"
        NHTSA[fa:fa-car NHTSA API<br/>REST Service]
        AutoDev[fa:fa-car-side Auto.dev API<br/>REST Service]
    end
    
    TG -->|Webhooks/Polling| Bot
    Bot -->|Bot API| TG
    Bot --> DI
    DI --> Cache
    Bot -->|HTTPS| NHTSA
    Bot -->|HTTPS + API Key| AutoDev
    Bot -.->|Future| Future_DB
    Bot -.->|Future| Future_Redis
    
    style Bot fill:#1168bd,color:#fff
    style DI fill:#1168bd,color:#fff
    style Cache fill:#1168bd,color:#fff
    style Future_DB fill:#cccccc,color:#666
    style Future_Redis fill:#cccccc,color:#666
```

### PlantUML Diagram
```plantuml
@startuml C4_Container
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Container Diagram - VIN Decoder Bot

Person(user, "Telegram User")

System_Boundary(vinbot, "VIN Decoder System") {
    Container(bot_app, "Bot Application", "Python 3.9+, asyncio", "Handles Telegram interactions and orchestrates VIN decoding")
    Container(di_container, "DI Container", "dependency-injector", "Manages component lifecycle and wiring")
    Container(cache, "In-Memory Cache", "Python collections", "Temporary storage for sessions and responses")
    Container(future_db, "PostgreSQL", "PostgreSQL 14", "Persistent storage (future)")
    Container(future_redis, "Redis Cache", "Redis 6", "Distributed cache (future)")
}

System_Ext(telegram, "Telegram API", "Bot API for messaging")
System_Ext(nhtsa, "NHTSA API", "Free VIN decoder")
System_Ext(autodev, "Auto.dev API", "Premium VIN decoder")

Rel(user, telegram, "Sends messages", "HTTPS")
Rel(telegram, bot_app, "Forwards messages", "Webhook/Polling")
Rel(bot_app, telegram, "Sends responses", "Bot API")
Rel(bot_app, di_container, "Uses", "In-process")
Rel(di_container, cache, "Manages", "In-process")
Rel(bot_app, nhtsa, "Queries", "REST/HTTPS")
Rel(bot_app, autodev, "Queries", "REST/HTTPS")
Rel_D(bot_app, future_db, "Stores", "SQL", $tags="future")
Rel_D(bot_app, future_redis, "Caches", "Redis Protocol", $tags="future")

@enduml
```

### Container Responsibilities

#### Bot Application
- **Technology**: Python 3.9+, python-telegram-bot, asyncio
- **Responsibilities**:
  - Telegram message handling
  - Command processing
  - Business logic orchestration
  - External API integration
  - Response formatting

#### DI Container
- **Technology**: dependency-injector
- **Responsibilities**:
  - Component lifecycle management
  - Dependency injection
  - Configuration management
  - Service registration

#### Cache Layer
- **Current**: In-memory Python dictionaries
- **Future**: Redis for distributed caching
- **Responsibilities**:
  - Session management
  - Response caching
  - Rate limiting data

## Level 3: Component Diagram

### Purpose
Shows the internal structure of the Bot Application container.

### Mermaid Diagram
```mermaid
graph TB
    subgraph "Presentation Layer"
        BotApp[Bot Application<br/>Main orchestrator]
        CmdHandlers[Command Handlers<br/>/start, /help, /vin]
        CallbackHandlers[Callback Handlers<br/>Button interactions]
        MessageAdapter[Message Adapter<br/>Format messages]
        KeyboardAdapter[Keyboard Adapter<br/>Build UI elements]
    end
    
    subgraph "Application Layer"
        CommandBus[Command Bus<br/>Route commands]
        QueryBus[Query Bus<br/>Route queries]
        VehicleAppService[Vehicle App Service<br/>Vehicle use cases]
        UserAppService[User App Service<br/>User use cases]
        DecodeVINHandler[Decode VIN Handler<br/>Process VIN decode]
        GetHistoryHandler[Get History Handler<br/>Retrieve history]
    end
    
    subgraph "Domain Layer"
        VehicleEntity[Vehicle Entity<br/>Core business object]
        VINValueObject[VIN Value Object<br/>VIN validation]
        UserEntity[User Entity<br/>User aggregate]
        VehicleRepo[Vehicle Repository<br/>Interface]
        UserRepo[User Repository<br/>Interface]
        DomainEvents[Domain Events<br/>Business events]
    end
    
    subgraph "Infrastructure Layer"
        NHTSAAdapter[NHTSA Adapter<br/>API integration]
        AutoDevAdapter[AutoDev Adapter<br/>API integration]
        DecoderFactory[Decoder Factory<br/>Service selection]
        InMemVehicleRepo[In-Memory Vehicle Repo<br/>Implementation]
        InMemUserRepo[In-Memory User Repo<br/>Implementation]
        EventBus[Event Bus<br/>Event publishing]
    end
    
    BotApp --> CmdHandlers
    BotApp --> CallbackHandlers
    CmdHandlers --> VehicleAppService
    VehicleAppService --> CommandBus
    CommandBus --> DecodeVINHandler
    DecodeVINHandler --> VehicleRepo
    DecodeVINHandler --> DecoderFactory
    DecoderFactory --> NHTSAAdapter
    DecoderFactory --> AutoDevAdapter
    VehicleRepo --> InMemVehicleRepo
    DecodeVINHandler --> EventBus
    EventBus --> DomainEvents
```

### PlantUML Component Diagram
```plantuml
@startuml C4_Component
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title Component Diagram - Bot Application

Container_Boundary(bot_app, "Bot Application") {
    Component(bot_main, "Bot Application", "Python", "Main entry point and orchestrator")
    Component(cmd_handlers, "Command Handlers", "Python", "Handle /start, /help, /vin commands")
    Component(callback_handlers, "Callback Handlers", "Python", "Handle inline keyboard interactions")
    Component(msg_adapter, "Message Adapter", "Python", "Format and compose messages")
    Component(kb_adapter, "Keyboard Adapter", "Python", "Build inline keyboards")
    
    Component(cmd_bus, "Command Bus", "Python", "Route and execute commands")
    Component(query_bus, "Query Bus", "Python", "Route and execute queries")
    Component(vehicle_service, "Vehicle App Service", "Python", "Orchestrate vehicle use cases")
    Component(user_service, "User App Service", "Python", "Orchestrate user use cases")
    
    Component(decode_handler, "Decode VIN Handler", "Python", "Execute VIN decode command")
    Component(history_handler, "Get History Handler", "Python", "Execute history query")
    
    Component(vehicle_entity, "Vehicle Entity", "Python", "Core vehicle domain model")
    Component(vin_vo, "VIN Value Object", "Python", "VIN validation and parsing")
    Component(user_entity, "User Entity", "Python", "User aggregate root")
    
    Component(decoder_factory, "Decoder Factory", "Python", "Select appropriate decoder service")
    Component(nhtsa_adapter, "NHTSA Adapter", "Python", "NHTSA API integration")
    Component(autodev_adapter, "AutoDev Adapter", "Python", "Auto.dev API integration")
    Component(event_bus, "Event Bus", "Python", "Publish domain events")
}

Rel(bot_main, cmd_handlers, "Delegates", "In-process")
Rel(bot_main, callback_handlers, "Delegates", "In-process")
Rel(cmd_handlers, vehicle_service, "Uses", "In-process")
Rel(vehicle_service, cmd_bus, "Dispatches", "In-process")
Rel(cmd_bus, decode_handler, "Routes", "In-process")
Rel(decode_handler, decoder_factory, "Uses", "In-process")
Rel(decoder_factory, nhtsa_adapter, "Creates", "In-process")
Rel(decoder_factory, autodev_adapter, "Creates", "In-process")
Rel(decode_handler, event_bus, "Publishes", "In-process")

@enduml
```

## Level 4: Code Level (Class Diagrams)

### Domain Model Class Diagram

```mermaid
classDiagram
    class Vehicle {
        -VehicleID id
        -VIN vin
        -VehicleInfo info
        -DateTime decoded_at
        -DecoderSource source
        +decode(decoder: VehicleDecoder) VehicleInfo
        +update_info(info: VehicleInfo) void
        +to_dict() dict
    }
    
    class VIN {
        -string value
        +is_valid() bool
        +get_year() int
        +get_manufacturer_code() string
        +get_vehicle_descriptor() string
        +get_check_digit() string
        +__str__() string
    }
    
    class User {
        -UserID id
        -TelegramID telegram_id
        -UserPreferences preferences
        -List~VehicleID~ history
        -DateTime created_at
        -DateTime updated_at
        +update_preferences(prefs: UserPreferences) void
        +add_to_history(vehicle_id: VehicleID) void
        +clear_history() void
        +get_recent_history(limit: int) List~VehicleID~
    }
    
    class VehicleInfo {
        +string make
        +string model
        +int year
        +string body_class
        +string vehicle_type
        +EngineSpecs engine
        +TransmissionInfo transmission
        +dict raw_data
        +merge(other: VehicleInfo) VehicleInfo
    }
    
    class VehicleRepository {
        <<interface>>
        +save(vehicle: Vehicle) void
        +find_by_id(id: VehicleID) Vehicle
        +find_by_vin(vin: VIN) Vehicle
        +find_recent(limit: int) List~Vehicle~
    }
    
    class UserRepository {
        <<interface>>
        +save(user: User) void
        +find_by_id(id: UserID) User
        +find_by_telegram_id(tid: TelegramID) User
        +delete(id: UserID) void
    }
    
    Vehicle --> VIN : contains
    Vehicle --> VehicleInfo : contains
    User --> Vehicle : references
    Vehicle ..> VehicleRepository : persisted by
    User ..> UserRepository : persisted by
```

### Application Layer Class Diagram

```mermaid
classDiagram
    class CommandBus {
        -dict handlers
        +register(command_type, handler) void
        +dispatch(command: Command) Result
    }
    
    class QueryBus {
        -dict handlers
        +register(query_type, handler) void
        +dispatch(query: Query) Result
    }
    
    class DecodeVINCommand {
        +VIN vin
        +UserID user_id
        +DecoderPreference decoder_preference
    }
    
    class GetVehicleHistoryQuery {
        +UserID user_id
        +int limit
    }
    
    class DecodeVINHandler {
        -VehicleRepository vehicle_repo
        -DecoderFactory decoder_factory
        -EventBus event_bus
        +handle(command: DecodeVINCommand) Vehicle
    }
    
    class GetVehicleHistoryHandler {
        -VehicleRepository vehicle_repo
        -UserRepository user_repo
        +handle(query: GetVehicleHistoryQuery) List~Vehicle~
    }
    
    class VehicleApplicationService {
        -CommandBus command_bus
        -QueryBus query_bus
        +decode_vin(vin: str, user_id: str) VehicleDTO
        +get_history(user_id: str) List~VehicleDTO~
    }
    
    CommandBus --> DecodeVINHandler : routes to
    QueryBus --> GetVehicleHistoryHandler : routes to
    VehicleApplicationService --> CommandBus : uses
    VehicleApplicationService --> QueryBus : uses
    DecodeVINHandler --> DecodeVINCommand : handles
    GetVehicleHistoryHandler --> GetVehicleHistoryQuery : handles
```

### Infrastructure Layer Class Diagram

```mermaid
classDiagram
    class DecoderFactory {
        -NHTSAAdapter nhtsa_adapter
        -AutoDevAdapter autodev_adapter
        +get_decoder(preference: DecoderPreference) VehicleDecoder
        +get_available_decoders() List~DecoderInfo~
    }
    
    class VehicleDecoder {
        <<interface>>
        +decode(vin: VIN) VehicleInfo
        +is_available() bool
        +get_name() string
    }
    
    class NHTSAAdapter {
        -NHTSAClient client
        +decode(vin: VIN) VehicleInfo
        +is_available() bool
        -transform_response(data: dict) VehicleInfo
    }
    
    class AutoDevAdapter {
        -AutoDevClient client
        -string api_key
        +decode(vin: VIN) VehicleInfo
        +is_available() bool
        -transform_response(data: dict) VehicleInfo
    }
    
    class NHTSAClient {
        -int timeout
        -Session session
        +decode_vin(vin: str) dict
        +get_makes() List~dict~
        +get_models(make: str) List~dict~
    }
    
    class AutoDevClient {
        -string api_key
        -int timeout
        -Session session
        +get_specs(vin: str) dict
        +get_market_value(vin: str) dict
        +get_history(vin: str) dict
    }
    
    DecoderFactory --> VehicleDecoder : creates
    NHTSAAdapter ..|> VehicleDecoder : implements
    AutoDevAdapter ..|> VehicleDecoder : implements
    NHTSAAdapter --> NHTSAClient : uses
    AutoDevAdapter --> AutoDevClient : uses
```

## Sequence Diagrams

### VIN Decode Sequence

```mermaid
sequenceDiagram
    participant User
    participant Telegram
    participant BotApp
    participant CmdHandler
    participant VehicleService
    participant CmdBus
    participant DecodeHandler
    participant DecoderFactory
    participant NHTSAAdapter
    participant VehicleRepo
    participant EventBus
    
    User->>Telegram: /vin 1HGCM82633A004352
    Telegram->>BotApp: Message update
    BotApp->>CmdHandler: Handle command
    CmdHandler->>VehicleService: decode_vin()
    VehicleService->>CmdBus: Dispatch DecodeVINCommand
    CmdBus->>DecodeHandler: Handle command
    DecodeHandler->>DecoderFactory: get_decoder()
    DecoderFactory->>DecodeHandler: Return NHTSAAdapter
    DecodeHandler->>NHTSAAdapter: decode(vin)
    NHTSAAdapter->>NHTSAAdapter: API call
    NHTSAAdapter->>DecodeHandler: Return VehicleInfo
    DecodeHandler->>VehicleRepo: save(vehicle)
    DecodeHandler->>EventBus: publish(VehicleDecoded)
    DecodeHandler->>VehicleService: Return Vehicle
    VehicleService->>CmdHandler: Return VehicleDTO
    CmdHandler->>BotApp: Format response
    BotApp->>Telegram: Send message
    Telegram->>User: Display vehicle info
```

### User Settings Update Sequence

```mermaid
sequenceDiagram
    participant User
    participant Telegram
    participant BotApp
    participant CallbackHandler
    participant UserService
    participant UserRepo
    participant EventBus
    
    User->>Telegram: Click settings button
    Telegram->>BotApp: Callback query
    BotApp->>CallbackHandler: Handle callback
    CallbackHandler->>UserService: get_preferences()
    UserService->>UserRepo: find_by_telegram_id()
    UserRepo->>UserService: Return User
    UserService->>CallbackHandler: Return preferences
    CallbackHandler->>BotApp: Build settings keyboard
    BotApp->>Telegram: Edit message
    Telegram->>User: Show settings menu
    User->>Telegram: Select decoder option
    Telegram->>BotApp: Callback query
    BotApp->>CallbackHandler: Handle selection
    CallbackHandler->>UserService: update_preferences()
    UserService->>UserRepo: save(user)
    UserService->>EventBus: publish(PreferencesUpdated)
    CallbackHandler->>BotApp: Confirmation
    BotApp->>Telegram: Update message
    Telegram->>User: Show confirmation
```

## Deployment Diagram

```mermaid
graph TB
    subgraph "Development Environment"
        DevMachine[Developer Machine<br/>MacOS/Linux/Windows]
        LocalBot[Local Bot Instance<br/>Python 3.9+]
        LocalCache[Local Cache<br/>In-Memory]
    end
    
    subgraph "Production Environment (AWS)"
        subgraph "Availability Zone 1"
            EC2_1[EC2 Instance<br/>Ubuntu 22.04]
            Bot1[Bot Container<br/>Docker]
        end
        
        subgraph "Availability Zone 2"
            EC2_2[EC2 Instance<br/>Ubuntu 22.04]
            Bot2[Bot Container<br/>Docker]
        end
        
        ALB[Application Load Balancer]
        ElastiCache[ElastiCache Redis<br/>Session Store]
        RDS[RDS PostgreSQL<br/>Data Persistence]
        S3[S3 Bucket<br/>Logs & Backups]
    end
    
    subgraph "Monitoring"
        CloudWatch[CloudWatch<br/>Metrics & Logs]
        Grafana[Grafana<br/>Dashboards]
    end
    
    subgraph "CI/CD"
        GitHub[GitHub<br/>Source Control]
        Actions[GitHub Actions<br/>CI/CD Pipeline]
        ECR[ECR<br/>Container Registry]
    end
    
    DevMachine --> LocalBot
    LocalBot --> LocalCache
    
    GitHub --> Actions
    Actions --> ECR
    ECR --> Bot1
    ECR --> Bot2
    
    ALB --> Bot1
    ALB --> Bot2
    Bot1 --> ElastiCache
    Bot2 --> ElastiCache
    Bot1 --> RDS
    Bot2 --> RDS
    Bot1 --> S3
    Bot2 --> S3
    Bot1 --> CloudWatch
    Bot2 --> CloudWatch
    CloudWatch --> Grafana
```

## Technology Stack Details

### Core Technologies
| Layer | Technology | Purpose |
|-------|------------|---------|
| Language | Python 3.9+ | Async support, type hints |
| Framework | python-telegram-bot | Telegram integration |
| DI Container | dependency-injector | IoC and dependency management |
| Validation | pydantic | Data validation and settings |
| Testing | pytest | Unit and integration testing |
| Async | asyncio | Concurrent operations |

### Infrastructure Technologies
| Component | Current | Future |
|-----------|---------|--------|
| Cache | In-memory dict | Redis/ElastiCache |
| Database | None | PostgreSQL/RDS |
| Container | Local Python | Docker |
| Orchestration | Manual | Kubernetes/ECS |
| Monitoring | Console logs | CloudWatch/Datadog |
| CI/CD | Manual | GitHub Actions |

### External Integrations
| Service | Protocol | Authentication |
|---------|----------|----------------|
| Telegram | HTTPS/Webhook | Bot Token |
| NHTSA | REST/HTTPS | None |
| Auto.dev | REST/HTTPS | API Key |

## Architecture Patterns Used

### Domain-Driven Design Patterns
- **Aggregates**: User, Vehicle
- **Value Objects**: VIN, VehicleID, UserID
- **Domain Events**: VehicleDecoded, UserRegistered
- **Repository Pattern**: Abstract persistence
- **Domain Services**: VIN validation logic

### Clean Architecture Patterns
- **Dependency Inversion**: Interfaces in domain
- **Use Cases**: Command and Query handlers
- **Ports and Adapters**: External service adapters
- **DTO Pattern**: Layer data transfer

### Enterprise Patterns
- **CQRS**: Command/Query separation
- **Event Bus**: Domain event publishing
- **Factory Pattern**: Decoder selection
- **Adapter Pattern**: External API integration
- **Strategy Pattern**: Decoder algorithms

## Security Considerations

### API Security
```mermaid
graph LR
    subgraph "Security Layers"
        Input[Input Validation]
        Auth[Authentication]
        RateLimit[Rate Limiting]
        Encryption[TLS Encryption]
        Secrets[Secret Management]
    end
    
    Request --> Input
    Input --> Auth
    Auth --> RateLimit
    RateLimit --> Encryption
    Encryption --> API
    API --> Secrets
```

### Data Flow Security
- **Input Validation**: VIN format validation
- **Authentication**: Telegram user verification
- **Rate Limiting**: Per-user request limits
- **Encryption**: TLS for all external calls
- **Secret Management**: Environment variables

## Performance Optimization

### Caching Strategy
```mermaid
graph TB
    Request[VIN Request]
    Cache{Cache Hit?}
    Service[Decoder Service]
    Store[Store in Cache]
    Response[Return Response]
    
    Request --> Cache
    Cache -->|Yes| Response
    Cache -->|No| Service
    Service --> Store
    Store --> Response
```

### Optimization Techniques
- **Response Caching**: Cache decoded VINs
- **Connection Pooling**: Reuse HTTP connections
- **Async Operations**: Non-blocking I/O
- **Batch Processing**: Group similar requests
- **Circuit Breaker**: Fail fast on errors

## Monitoring and Observability

### Metrics Collection
```mermaid
graph TB
    subgraph "Application Metrics"
        Requests[Request Count]
        Latency[Response Time]
        Errors[Error Rate]
        Cache[Cache Hit Rate]
    end
    
    subgraph "Business Metrics"
        Users[Active Users]
        VINs[VINs Decoded]
        Services[Service Usage]
    end
    
    subgraph "System Metrics"
        CPU[CPU Usage]
        Memory[Memory Usage]
        Network[Network I/O]
    end
    
    Requests --> Dashboard
    Latency --> Dashboard
    Errors --> Dashboard
    Cache --> Dashboard
    Users --> Dashboard
    VINs --> Dashboard
    Services --> Dashboard
    CPU --> Dashboard
    Memory --> Dashboard
    Network --> Dashboard
    
    Dashboard[Monitoring Dashboard]
```

## References

- [C4 Model](https://c4model.com/) - The C4 model for visualizing software architecture
- [Mermaid](https://mermaid-js.github.io/) - Diagram syntax documentation
- [PlantUML](https://plantuml.com/) - UML diagram tool
- [Structurizr](https://structurizr.com/) - Software architecture workspace

---

*Last Updated: January 2025*  
*Version: 1.0.0*