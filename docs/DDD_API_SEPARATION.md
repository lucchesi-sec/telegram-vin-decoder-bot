# DDD-Compliant API Layer Separation

## Overview

This document describes the implementation of proper API layer separation following Domain-Driven Design (DDD) principles. The refactoring ensures clear boundaries between presentation layers while maintaining domain purity.

## Architecture Principles

### 1. Domain Layer Isolation
- **Domain entities and value objects** remain pure business logic
- **No dependencies** on presentation or infrastructure concerns
- **Application services** act as the boundary between domain and presentation

### 2. Presentation Layer Separation
- **API layer** (`src/presentation/api/`) provides REST endpoints
- **Telegram bot** (`src/presentation/telegram_bot/`) handles Telegram-specific interactions
- **Web dashboard** (`src/presentation/web-dashboard-next/`) provides web interface
- **Shared components** (`src/presentation/shared/`) contain common presentation logic

### 3. Unified Authentication
- **JWT-based authentication** works across all presentation layers
- **Shared auth utilities** in `src/presentation/shared/auth/`
- **Consistent user context** throughout the application

## Directory Structure

```
src/presentation/
├── api/                    # REST API (FastAPI)
│   ├── routes/            # Modular route definitions
│   │   ├── auth_routes.py     # Authentication endpoints
│   │   ├── vehicle_routes.py  # Vehicle-related endpoints
│   │   ├── user_routes.py     # User-related endpoints
│   │   └── health_routes.py   # Health check endpoints
│   ├── middleware/        # API middleware
│   │   ├── cors.py           # CORS configuration
│   │   └── error_handling.py # Error handling middleware
│   ├── dependencies/      # Dependency injection
│   │   └── container.py      # DI container integration
│   └── server.py          # Main FastAPI application
├── telegram_bot/          # Telegram interface
│   ├── handlers/          # Message and command handlers
│   ├── keyboards/         # Telegram keyboards
│   ├── formatters/        # Message formatters
│   └── adapters/          # Telegram-specific adapters
├── web-dashboard-next/    # Web interface (Next.js)
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   └── lib/              # Client-side utilities
└── shared/               # Common presentation components
    ├── dto/              # Data Transfer Objects
    │   ├── vehicle_dto.py    # Vehicle DTOs
    │   └── user_dto.py       # User DTOs
    ├── auth/             # Authentication utilities
    │   └── jwt_handler.py    # JWT token handling
    └── adapters/         # Shared adapters
        └── api_client.py     # Internal API client
```

## Key Components

### 1. Modular API Routes

Each domain context has its own route module:

- **`auth_routes.py`**: Handles authentication and JWT token management
- **`vehicle_routes.py`**: Vehicle decoding and management endpoints
- **`user_routes.py`**: User profile and preferences endpoints
- **`health_routes.py`**: System health and monitoring endpoints

### 2. Data Transfer Objects (DTOs)

DTOs provide a clean boundary between domain entities and API responses:

```python
# Example: VehicleResponseDTO
class VehicleResponseDTO(BaseModel):
    id: Optional[int] = None
    vin: str
    manufacturer: Optional[str] = None
    # ... other fields
    
    @classmethod
    def from_domain(cls, vehicle: Vehicle) -> "VehicleResponseDTO":
        """Convert domain Vehicle entity to DTO."""
        return cls(
            id=vehicle.id.value if vehicle.id else None,
            vin=vehicle.vin.value,
            # ... map other fields
        )
```

### 3. Unified Authentication

JWT-based authentication system that works across all presentation layers:

```python
# Authentication flow
1. User authenticates via /api/auth/telegram
2. Receives JWT token
3. Token used for all subsequent API calls
4. Both web dashboard and Telegram bot use same auth system
```

### 4. Internal API Client

Shared client for communication between presentation layers:

```python
# Usage in Telegram bot
api_client = InternalAPIClient(base_url="http://api:5000")
await api_client.authenticate_telegram_user(telegram_id, username)
result = await api_client.decode_vin(vin)
```

## Benefits of This Approach

### 1. **Domain Purity**
- Domain logic remains isolated from presentation concerns
- Business rules are consistent across all interfaces
- Easy to test domain logic in isolation

### 2. **Clear Boundaries**
- Each presentation layer has well-defined responsibilities
- No direct dependencies between Telegram bot and web dashboard
- Shared logic is explicitly placed in shared modules

### 3. **Maintainability**
- Changes to business logic automatically apply to all interfaces
- New presentation layers can be added easily
- Modular structure makes code easier to understand and modify

### 4. **Scalability**
- API can be scaled independently of other components
- Different teams can work on different presentation layers
- Easy to add new endpoints or modify existing ones

### 5. **Testability**
- Each layer can be tested independently
- Mock implementations can be easily created
- Integration tests can verify end-to-end functionality

## Migration Path

### Phase 1: API Structure (Completed)
- ✅ Created modular API routes
- ✅ Implemented unified authentication
- ✅ Added shared DTOs and adapters
- ✅ Updated Docker configuration

### Phase 2: Telegram Bot Integration
- 🔄 Update Telegram bot to use internal API client
- 🔄 Implement JWT authentication for bot users
- 🔄 Remove direct domain service dependencies from bot

### Phase 3: Web Dashboard Integration
- 🔄 Ensure web dashboard uses new API structure
- 🔄 Implement proper authentication flow
- 🔄 Add error handling and loading states

### Phase 4: Enhanced Features
- 🔄 Add OpenAPI documentation
- 🔄 Implement rate limiting
- 🔄 Add comprehensive logging and monitoring
- 🔄 Implement proper pagination

## Usage Examples

### Starting the API Server

```bash
# Development
python start_api_server.py

# Production
python -m uvicorn src.presentation.api.server:app --host 0.0.0.0 --port 5000

# Docker
docker-compose up api
```

### API Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Authenticate Telegram user
curl -X POST http://localhost:5000/api/auth/telegram \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456, "username": "testuser"}'

# Decode VIN (requires authentication)
curl -X POST http://localhost:5000/api/vehicles/decode \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"vin": "1HGBH41JXMN109186"}'

# Get user vehicles
curl http://localhost:5000/api/vehicles?page=1&limit=10 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Testing

```bash
# Test the new API structure
python -m pytest src/tests/integration/test_api_separation.py

# Test authentication
python -m pytest src/tests/unit/presentation/test_auth_routes.py

# Test DTOs
python -m pytest src/tests/unit/presentation/test_dto_mapping.py
```

## Next Steps

1. **Complete Telegram bot integration** with the new API structure
2. **Add comprehensive error handling** and validation
3. **Implement proper user context** extraction from JWT tokens
4. **Add OpenAPI documentation** with Swagger UI
5. **Implement rate limiting** and security middleware
6. **Add comprehensive logging** and monitoring
7. **Create integration tests** for the complete flow

---

This implementation follows DDD principles by maintaining clear separation of concerns while providing a unified, scalable API layer that both the web dashboard and Telegram bot can consume.