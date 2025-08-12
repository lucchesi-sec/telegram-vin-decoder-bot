# Architecture Documentation - VIN Decoder Telegram Bot

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architectural Principles](#architectural-principles)
4. [Architecture Style](#architecture-style)
5. [System Context](#system-context)
6. [Container Architecture](#container-architecture)
7. [Component Architecture](#component-architecture)
8. [Data Architecture](#data-architecture)
9. [Infrastructure Architecture](#infrastructure-architecture)
10. [Security Architecture](#security-architecture)
11. [Architecture Decision Records](#architecture-decision-records)
12. [Quality Attributes](#quality-attributes)
13. [Future Roadmap](#future-roadmap)

## Executive Summary

The VIN Decoder Telegram Bot is a modern, microservices-ready application built using Domain-Driven Design (DDD) principles and Clean Architecture patterns. It provides vehicle information decoding services through a conversational Telegram interface, integrating with multiple external VIN decoder APIs.

### Key Architectural Highlights
- **Domain-Driven Design**: Clear separation of business logic into bounded contexts
- **Clean Architecture**: Layered architecture with dependency inversion
- **Event-Driven Communication**: Asynchronous message passing between components
- **Dependency Injection**: IoC container for flexible component wiring
- **Adapter Pattern**: External service integration through standardized interfaces
- **CQRS Pattern**: Command and Query separation for scalability

## System Overview

### Purpose
Provide instant, accurate vehicle information through VIN decoding via a user-friendly Telegram bot interface.

### Core Capabilities
- Real-time VIN decoding from multiple data sources
- User preference management and history tracking
- Rich conversational interface with inline keyboards
- Flexible service provider selection (NHTSA, Auto.dev)
- Comprehensive vehicle specification reporting

### Technical Stack

#### Backend
- **Language**: Python 3.9+
- **Framework**: python-telegram-bot (async)
- **Web Framework**: FastAPI (REST API)
- **Architecture**: DDD + Clean Architecture
- **DI Container**: dependency-injector
- **Database**: PostgreSQL (production), SQLite (development)
- **ORM**: SQLAlchemy
- **External APIs**: NHTSA, Auto.dev
- **Testing**: pytest, pytest-asyncio
- **Configuration**: pydantic-settings

#### Frontend (Web Dashboard)
- **Framework**: Next.js 15.4 (React 19)
- **Language**: TypeScript
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS 3.4
- **State Management**: React hooks
- **Build Tool**: Next.js with Turbo
- **Package Manager**: npm

## Architectural Principles

### 1. Domain-Driven Design (DDD)
- **Bounded Contexts**: Clear domain boundaries (Vehicle, User, Messaging, Integration)
- **Ubiquitous Language**: Consistent terminology across code and documentation
- **Domain Events**: Event-driven communication between aggregates
- **Value Objects**: Immutable domain concepts (VIN, UserID, etc.)

### 2. Clean Architecture (Hexagonal)
- **Dependency Inversion**: Core domain independent of external concerns
- **Ports and Adapters**: Clear interfaces for external integrations
- **Use Case Driven**: Application layer orchestrates business operations
- **Framework Independence**: Core logic decoupled from frameworks

### 3. SOLID Principles
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Implementations are interchangeable
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### 4. Event-Driven Architecture
- **Domain Events**: Business events trigger cross-aggregate communication
- **Event Bus**: Decoupled event publishing and subscription
- **Eventual Consistency**: Asynchronous updates across boundaries
- **Event Sourcing Ready**: Foundation for event sourcing if needed

## Architecture Style

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│    (Telegram Bot, REST API, Next.js Dashboard, CLI)        │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                        │
│     (Use Cases, Command Handlers, Query Handlers)          │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                           │
│    (Entities, Value Objects, Domain Services, Events)      │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                      │
│  (Repositories, External Services, Messaging, Persistence)  │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Flow
- Dependencies point inward toward the domain
- Domain layer has no external dependencies
- Application layer depends only on domain
- Infrastructure and presentation depend on application and domain

## System Context

### C4 Model - Level 1: System Context

```mermaid
graph TB
    User[Telegram User]
    Bot[VIN Decoder Bot System]
    Telegram[Telegram API]
    NHTSA[NHTSA VIN API]
    AutoDev[Auto.dev API]
    
    User -->|Sends VIN queries| Bot
    Bot -->|Returns vehicle info| User
    Bot -->|Bot API calls| Telegram
    Telegram -->|Updates/Messages| Bot
    Bot -->|VIN lookup| NHTSA
    Bot -->|Premium VIN lookup| AutoDev
```

### External Systems
1. **Telegram Platform**: Message delivery and user interaction
2. **NHTSA API**: Free government VIN decoder service
3. **Auto.dev API**: Premium vehicle data provider
4. **Future**: Analytics, monitoring, payment systems

## Container Architecture

### C4 Model - Level 2: Container Diagram

```mermaid
graph TB
    subgraph "VIN Decoder System"
        Bot[Telegram Bot Application<br/>Python, Async]
        DI[Dependency Injection Container<br/>dependency-injector]
        Cache[In-Memory Cache<br/>Python Dict]
    end
    
    subgraph "External Services"
        TG[Telegram API]
        NHTSA[NHTSA API]
        AutoDev[Auto.dev API]
    end
    
    Bot --> DI
    DI --> Cache
    Bot -->|HTTPS| TG
    Bot -->|HTTPS| NHTSA
    Bot -->|HTTPS| AutoDev
```

### Container Descriptions

#### Telegram Bot Application
- **Technology**: Python 3.9+, asyncio
- **Responsibility**: Core application logic and orchestration
- **Communication**: HTTPS REST/Webhook with Telegram

#### Web Dashboard (Next.js)
- **Technology**: Next.js 15.4, React 19, TypeScript
- **Responsibility**: Web-based vehicle management interface
- **Communication**: REST API calls to FastAPI backend
- **UI Framework**: shadcn/ui with Tailwind CSS
- **Features**: Real-time statistics, VIN decoding, search, vehicle management

#### REST API (FastAPI)
- **Technology**: FastAPI, SQLAlchemy
- **Responsibility**: HTTP API for web dashboard and external integrations
- **Communication**: JSON REST over HTTPS
- **Endpoints**: Vehicle CRUD, VIN decoding, statistics

#### Dependency Injection Container
- **Technology**: dependency-injector
- **Responsibility**: Component wiring and lifecycle management
- **Pattern**: Constructor injection

#### Database Layer
- **Technology**: PostgreSQL (production), SQLite (dev)
- **Responsibility**: Persistent storage for vehicles and users
- **ORM**: SQLAlchemy for database abstraction

#### In-Memory Cache
- **Technology**: Python collections
- **Responsibility**: Temporary storage for user sessions
- **Future**: Redis/Upstash for persistence

## Component Architecture

### C4 Model - Level 3: Component Diagram

```mermaid
graph TB
    subgraph "Presentation Layer"
        BotApp[Bot Application]
        CmdHandler[Command Handlers]
        CallbackHandler[Callback Handlers]
        MsgAdapter[Message Adapter]
        KbAdapter[Keyboard Adapter]
        WebDashboard[Next.js Dashboard]
        RestAPI[FastAPI REST Service]
    end
    
    subgraph "Application Layer"
        CmdBus[Command Bus]
        QueryBus[Query Bus]
        VehicleService[Vehicle App Service]
        UserService[User App Service]
        DecodeCmd[Decode VIN Command]
        GetHistoryQuery[Get History Query]
    end
    
    subgraph "Domain Layer"
        Vehicle[Vehicle Entity]
        VIN[VIN Value Object]
        User[User Entity]
        VehicleRepo[Vehicle Repository]
        UserRepo[User Repository]
        DomainEvents[Domain Events]
    end
    
    subgraph "Infrastructure Layer"
        NHTSAClient[NHTSA Client]
        AutoDevClient[AutoDev Client]
        DecoderFactory[Decoder Factory]
        InMemRepo[In-Memory Repositories]
        EventBus[Event Bus Implementation]
    end
    
    BotApp --> CmdHandler
    BotApp --> CallbackHandler
    CmdHandler --> VehicleService
    VehicleService --> CmdBus
    CmdBus --> DecodeCmd
    DecodeCmd --> VehicleRepo
    DecodeCmd --> DecoderFactory
    DecoderFactory --> NHTSAClient
    DecoderFactory --> AutoDevClient
```

### Key Components

#### Domain Layer Components
- **Vehicle Entity**: Core business object representing decoded vehicle
- **VIN Value Object**: Immutable VIN with validation
- **User Entity**: User preferences and history
- **Domain Services**: Business logic not fitting entities
- **Repository Interfaces**: Abstraction for data persistence

#### Application Layer Components
- **Command Handlers**: Execute business operations
- **Query Handlers**: Retrieve data without side effects
- **Application Services**: Orchestrate use cases
- **Command/Query Bus**: Message routing and handling
- **DTOs**: Data transfer between layers

#### Infrastructure Components
- **External Service Clients**: API integration implementations
- **Repository Implementations**: Concrete data access
- **Adapters**: Convert between external and domain models
- **Event Bus**: Concrete event publishing/subscription

#### Presentation Components

##### Telegram Bot Components
- **Bot Application**: Main Telegram bot orchestrator
- **Command Handlers**: Handle Telegram commands (/start, /vin)
- **Callback Handlers**: Handle inline keyboard interactions
- **Message Formatters**: Rich message composition
- **Keyboard Builders**: Dynamic UI generation

##### Web Dashboard Components (Next.js)
- **Page Components**: Server and client React components
- **UI Components**: shadcn/ui component library
- **API Client**: Fetch-based REST client for backend communication
- **State Management**: React hooks for local state
- **Table Component**: Paginated vehicle display with search
- **Dialog Components**: Modal interfaces for VIN decoding and details
- **Card Components**: Statistics and data visualization

##### REST API Components (FastAPI)
- **API Router**: HTTP endpoint routing and validation
- **Request Handlers**: Process HTTP requests and responses
- **CORS Middleware**: Cross-origin resource sharing configuration
- **Response Models**: Pydantic models for API responses
- **Error Handlers**: Standardized error responses

## Data Architecture

### Domain Model

```mermaid
classDiagram
    class Vehicle {
        +VehicleID id
        +VIN vin
        +VehicleInfo info
        +DecodedAt decoded_at
        +decode()
    }
    
    class VIN {
        +String value
        +is_valid()
        +get_year()
        +get_manufacturer()
    }
    
    class User {
        +UserID id
        +TelegramID telegram_id
        +UserPreferences preferences
        +List~VehicleID~ history
        +update_preferences()
        +add_to_history()
    }
    
    class VehicleInfo {
        +String make
        +String model
        +Int year
        +EngineSpecs engine
        +Dict specs
    }
    
    Vehicle --> VIN
    Vehicle --> VehicleInfo
    User --> Vehicle
```

### Data Flow Patterns

#### VIN Decode Flow
1. User sends VIN via Telegram message
2. Command handler validates and creates DecodeVIN command
3. Command bus routes to DecodeVINHandler
4. Handler uses DecoderFactory to select appropriate service
5. External service adapter fetches and transforms data
6. Vehicle entity created and persisted
7. VehicleDecoded event published
8. Response formatted and sent to user

#### User Settings Flow
1. User clicks settings button
2. Callback handler retrieves user preferences
3. Dynamic keyboard generated based on current state
4. User selection updates preferences
5. UserPreferencesUpdated event published
6. UI refreshed with new settings

### Persistence Strategy

#### Current Implementation
- **In-Memory Repositories**: Fast, simple, suitable for MVP
- **No external database**: Reduces complexity
- **Session-based storage**: Data lives for bot lifetime

#### Future Migration Path
1. **Phase 1**: Add Redis for session caching
2. **Phase 2**: PostgreSQL for persistent storage
3. **Phase 3**: Event sourcing for audit trail
4. **Phase 4**: Read model projections for queries

## Infrastructure Architecture

### Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer]
        Bot1[Bot Instance 1]
        Bot2[Bot Instance 2]
        Redis[Redis Cache]
        PG[PostgreSQL]
    end
    
    subgraph "External Services"
        TG[Telegram Servers]
        NHTSA[NHTSA API]
        AutoDev[Auto.dev API]
    end
    
    subgraph "Monitoring"
        Logs[Log Aggregation]
        Metrics[Metrics Collection]
        Alerts[Alert Manager]
    end
    
    TG -->|Webhook| LB
    LB --> Bot1
    LB --> Bot2
    Bot1 --> Redis
    Bot2 --> Redis
    Bot1 --> PG
    Bot2 --> PG
    Bot1 --> Logs
    Bot2 --> Logs
```

### Scalability Considerations

#### Horizontal Scaling
- Stateless bot instances
- Shared cache layer (Redis)
- Database connection pooling
- Load balancer distribution

#### Performance Optimization
- Response caching for repeated VINs
- Connection pooling for external APIs
- Async/await for concurrent operations
- Batch processing for bulk operations

### Monitoring and Observability

#### Logging Strategy
- Structured logging with context
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for request tracing
- External service call logging

#### Metrics Collection
- Request/response times
- API call success rates
- Cache hit ratios
- Error rates by type

#### Health Checks
- Liveness probe: Bot connection status
- Readiness probe: External service availability
- Dependency health aggregation

## Web Dashboard Architecture

### Frontend Architecture (Next.js)

#### Technology Stack
- **Framework**: Next.js 15.4 with App Router
- **UI Library**: React 19 with TypeScript
- **Component Library**: shadcn/ui (built on Radix UI)
- **Styling**: Tailwind CSS 3.4 with custom design system
- **State Management**: React hooks (useState, useEffect)
- **Data Fetching**: Native fetch API with async/await

#### Component Structure
```
web-dashboard-next/
├── app/                      # Next.js App Router
│   ├── page.tsx             # Main dashboard page
│   ├── layout.tsx           # Root layout with metadata
│   └── globals.css          # Global styles and Tailwind
├── components/
│   └── ui/                  # shadcn/ui components
│       ├── button.tsx       # Button component
│       ├── card.tsx         # Card component
│       ├── dialog.tsx       # Modal dialog
│       ├── table.tsx        # Data table
│       ├── tabs.tsx         # Tab navigation
│       ├── input.tsx        # Form inputs
│       └── badge.tsx        # Status badges
├── lib/
│   └── utils.ts            # Utility functions (cn)
└── public/                  # Static assets
```

#### Key Features
1. **Real-time Statistics Dashboard**
   - Total vehicles card
   - Unique manufacturers count
   - Recent decodes (24h) tracking

2. **Vehicle Management Table**
   - Paginated data display
   - Search/filter functionality
   - Sort by columns
   - Inline actions (view, delete)

3. **VIN Decoding Interface**
   - Modal-based input form
   - Real-time validation
   - Error handling with user feedback
   - Success notifications

4. **Vehicle Details View**
   - Tabbed interface (Basic, Technical, Raw Data)
   - Comprehensive information display
   - JSON data viewer for raw responses

#### Design System
- **Color Palette**: Purple to pink gradient theme
- **Typography**: System font stack with fallbacks
- **Spacing**: Consistent 4px grid system
- **Components**: Modern card-based layout
- **Responsive**: Mobile-first responsive design
- **Dark Mode**: CSS variables for theme switching (ready)

#### Performance Optimizations
- **Server Components**: Default for static content
- **Client Components**: Only for interactive features
- **Code Splitting**: Automatic per-route splitting
- **Image Optimization**: Next.js Image component
- **Font Optimization**: System fonts for performance

### API Integration

#### REST API Endpoints
```typescript
// Vehicle endpoints
GET    /api/vehicles         // List vehicles (paginated)
GET    /api/vehicles/:id     // Get single vehicle
POST   /api/decode           // Decode new VIN
DELETE /api/vehicles/:id     // Delete vehicle
GET    /api/stats           // Dashboard statistics

// Health checks
GET    /health              // Service health status
```

#### Data Models
```typescript
interface Vehicle {
  id: number
  vin: string
  manufacturer: string
  model: string
  year: number
  vehicle_type: string
  engine_info: string
  fuel_type: string
  decoded_at: string
  user_id: number
  raw_data: any
}

interface Stats {
  total_vehicles: number
  unique_manufacturers: number
  recent_decodes: number
}
```

### Deployment Architecture

#### Development Setup
```bash
# Install dependencies
cd src/presentation/web-dashboard-next
npm install

# Run development server
npm run dev  # Runs on http://localhost:3000
```

#### Production Build
```bash
# Build for production
npm run build

# Start production server
npm start
```

#### Docker Deployment
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Migration from Legacy Dashboard

#### Legacy Stack (Deprecated)
- Vanilla JavaScript with jQuery-like patterns
- Server-side HTML templates
- CSS with custom styles
- FastAPI template rendering

#### New Stack (Current)
- React with TypeScript
- shadcn/ui component library
- Tailwind CSS utility-first styling
- Next.js with API routes
- Server and Client components

#### Migration Benefits
- **Type Safety**: Full TypeScript support
- **Component Reusability**: Modular UI components
- **Better UX**: Smoother interactions and loading states
- **Modern Tooling**: Hot reload, fast refresh, better DX
- **Performance**: Optimized bundle sizes and loading
- **Maintainability**: Clear component structure

## Security Architecture

### Security Layers

```mermaid
graph TB
    subgraph "Security Perimeter"
        WAF[Web Application Firewall]
        RateLimit[Rate Limiting]
        Auth[Authentication]
        Authz[Authorization]
        Encryption[Encryption Layer]
    end
    
    subgraph "Application Security"
        InputVal[Input Validation]
        Sanitize[Output Sanitization]
        Secrets[Secret Management]
        Audit[Audit Logging]
    end
    
    User -->|HTTPS| WAF
    WAF --> RateLimit
    RateLimit --> Auth
    Auth --> Authz
    Authz --> InputVal
```

### Security Measures

#### API Security
- **Token Management**: Secure storage of API keys
- **Rate Limiting**: Prevent API abuse
- **Request Validation**: Input sanitization
- **HTTPS Only**: Encrypted communication

#### Data Protection
- **PII Handling**: No persistent storage of personal data
- **VIN Privacy**: Optional anonymization
- **User Isolation**: Tenant data separation
- **Audit Trail**: Security event logging

#### Telegram Security
- **Bot Token**: Environment variable storage
- **User Verification**: Telegram ID validation
- **Command Injection**: Input sanitization
- **Message Limits**: Prevent spam/abuse

### Compliance Considerations
- GDPR: Right to erasure, data minimization
- CCPA: User data transparency
- Industry: Automotive data standards
- Platform: Telegram bot guidelines

## Architecture Decision Records

### ADR-001: Domain-Driven Design Adoption
**Status**: Accepted  
**Context**: Need clear separation of business logic  
**Decision**: Implement DDD with bounded contexts  
**Consequences**: Higher initial complexity, better maintainability  

### ADR-002: Clean Architecture Layers
**Status**: Accepted  
**Context**: Require flexibility for future changes  
**Decision**: Implement hexagonal architecture with clear layers  
**Consequences**: More boilerplate, better testability  

### ADR-003: Dependency Injection Container
**Status**: Accepted  
**Context**: Need flexible component wiring  
**Decision**: Use dependency-injector library  
**Consequences**: Runtime overhead, improved modularity  

### ADR-004: In-Memory Storage Initially
**Status**: Accepted  
**Context**: MVP needs quick deployment  
**Decision**: Start with in-memory, migrate later  
**Consequences**: Data loss on restart, simple deployment  

### ADR-005: CQRS Pattern Implementation
**Status**: Accepted  
**Context**: Different read/write patterns  
**Decision**: Separate commands and queries  
**Consequences**: More classes, clearer intent  

### ADR-006: Event-Driven Communication
**Status**: Accepted  
**Context**: Need loose coupling between components  
**Decision**: Implement domain events and event bus  
**Consequences**: Async complexity, better scalability  

## Quality Attributes

### Performance Requirements
- **Response Time**: < 2 seconds for VIN decode
- **Throughput**: 100 requests/minute per instance
- **Concurrency**: 50 simultaneous users
- **Cache Hit Ratio**: > 30% for common VINs

### Reliability Requirements
- **Availability**: 99.9% uptime
- **Error Rate**: < 1% failed requests
- **Recovery Time**: < 5 minutes
- **Data Consistency**: Eventual consistency

### Scalability Requirements
- **Horizontal Scaling**: Support multiple instances
- **Load Distribution**: Even request distribution
- **Database Scaling**: Read replicas support
- **Cache Scaling**: Distributed caching ready

### Maintainability Requirements
- **Code Coverage**: > 80% test coverage
- **Documentation**: Comprehensive inline docs
- **Modularity**: Loosely coupled components
- **Debugging**: Structured logging and tracing

### Security Requirements
- **Authentication**: Telegram user verification
- **Authorization**: User-specific data access
- **Encryption**: TLS for all external communication
- **Audit**: Security event logging

## Future Roadmap

### Phase 1: Foundation Enhancement (Current)
- ✅ DDD implementation
- ✅ Clean architecture
- ✅ Basic VIN decoding
- ✅ Telegram integration
- ⏳ Comprehensive testing
- ⏳ Documentation completion

### Phase 2: Persistence Layer (Q1 2025)
- [ ] Redis integration for caching
- [ ] PostgreSQL for data persistence
- [ ] Migration scripts
- [ ] Backup strategies
- [ ] Data retention policies

### Phase 3: Advanced Features (Q2 2025)
- [ ] Vehicle history tracking
- [ ] Price estimation service
- [ ] Recall information
- [ ] Maintenance schedules
- [ ] Multi-language support

### Phase 4: Enterprise Features (Q3 2025)
- [ ] REST API endpoint
- [ ] Webhook support
- [ ] Batch processing
- [ ] Analytics dashboard
- [ ] White-label solution

### Phase 5: AI Enhancement (Q4 2025)
- [ ] Natural language processing
- [ ] Predictive maintenance
- [ ] Image-based VIN detection
- [ ] Conversational AI
- [ ] Recommendation engine

## Appendices

### A. Technology Decisions
- **Python 3.9+**: Modern async support, type hints
- **python-telegram-bot**: Mature, async-first library
- **dependency-injector**: Powerful DI with good Python integration
- **pydantic**: Data validation and settings management
- **pytest**: Comprehensive testing framework

### B. Development Practices
- **Git Flow**: Feature branches, PR reviews
- **Semantic Versioning**: Clear version management
- **Continuous Integration**: Automated testing
- **Code Review**: Mandatory peer review
- **Documentation**: Code-as-documentation approach

### C. Operational Procedures
- **Deployment**: Blue-green deployment strategy
- **Monitoring**: Proactive alerting
- **Incident Response**: Defined escalation paths
- **Backup**: Regular data backups
- **Disaster Recovery**: RTO < 1 hour

### D. References
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [C4 Model - Simon Brown](https://c4model.com/)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [Dependency Injector Documentation](https://python-dependency-injector.ets-labs.org/)

---

*Last Updated: January 2025*  
*Version: 1.0.0*  
*Maintainer: Engineering Team*