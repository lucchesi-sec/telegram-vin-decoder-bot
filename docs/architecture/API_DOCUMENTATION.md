# API Documentation - VIN Decoder Bot

## Overview
This document provides comprehensive API documentation for the VIN Decoder Bot, including internal service APIs, external API integrations, and the Telegram bot command interface.

## Table of Contents
1. [Telegram Bot Commands](#telegram-bot-commands)
2. [Web Dashboard REST API](#web-dashboard-rest-api)
3. [Internal Service APIs](#internal-service-apis)
4. [External API Integrations](#external-api-integrations)
5. [Event APIs](#event-apis)
6. [Error Codes](#error-codes)
7. [Rate Limiting](#rate-limiting)
8. [Future Enhancements](#future-enhancements)

## Telegram Bot Commands

### User Commands

#### `/start`
Initializes bot interaction and registers user.

**Usage:** `/start`

**Response:**
```
🚗 Welcome to VIN Decoder Bot!

I can help you decode Vehicle Identification Numbers (VINs) to get detailed information about vehicles.

Simply send me a 17-character VIN, and I'll provide:
• Make, Model, and Year
• Engine specifications
• Vehicle type and body style
• Manufacturing details

Try it now: Send me a VIN or use /vin <VIN>

Current decoder: NHTSA (Free)
```

#### `/vin <VIN>`
Decodes a vehicle identification number.

**Usage:** `/vin 1HGCM82633A004352`

**Parameters:**
- `VIN` (required): 17-character alphanumeric vehicle identification number

**Response:**
```
🚗 Vehicle Information

VIN: 1HGCM82633A004352
Year: 2003
Make: HONDA
Model: Accord
Type: PASSENGER CAR
Body: Sedan/Saloon

🔧 Engine:
• Displacement: 2.4L
• Cylinders: 4
• Fuel Type: Gasoline

📍 Manufacturing:
• Plant: Marysville
• Country: United States

Decoded via: NHTSA
```

**Inline Keyboard:**
```
[🔄 Refresh] [💾 Save] [📊 More Info]
[⚙️ Settings] [📜 History]
```

#### `/help`
Shows available commands and usage instructions.

**Usage:** `/help`

**Response:**
```
📖 VIN Decoder Bot Help

Commands:
• /start - Start the bot
• /vin <VIN> - Decode a VIN
• /help - Show this help message
• /settings - Configure preferences
• /history - View recent VINs
• /saved - View saved vehicles

You can also just send a VIN directly without any command!

Examples:
• /vin 1HGCM82633A004352
• WBA3B5C50FF970265

Need support? Contact @support
```

#### `/settings`
Opens user settings menu.

**Usage:** `/settings`

**Response with Inline Keyboard:**
```
⚙️ Settings

Current Configuration:
• Decoder Service: NHTSA
• History Limit: 10
• Auto-save: Off

Select an option to configure:
```

**Keyboard Layout:**
```
[🔧 Decoder Service]
[📊 History Limit] [💾 Auto-save]
[🔔 Notifications] [🌍 Language]
[↩️ Back]
```

#### `/history`
Shows recently decoded VINs.

**Usage:** `/history [limit]`

**Parameters:**
- `limit` (optional): Number of recent VINs to show (default: 5, max: 20)

**Response:**
```
📜 Recent VINs

1. 1HGCM82633A004352
   2003 Honda Accord - 5 minutes ago
   
2. WBA3B5C50FF970265
   2015 BMW 3 Series - 2 hours ago
   
3. JH4KA7650PC003452
   1993 Acura Legend - Yesterday

[View All] [Clear History]
```

#### `/saved`
Shows saved vehicles.

**Usage:** `/saved`

**Response:**
```
💾 Saved Vehicles

1. My Car - 2003 Honda Accord
   VIN: 1HGCM82633A004352
   
2. Work Van - 2018 Ford Transit
   VIN: 1FTBW2CM6JKA12345

[Manage Saved]
```

### Callback Queries

#### Decoder Selection
**Data:** `settings:decoder:{service}`

**Services:**
- `nhtsa` - NHTSA free service
- `autodev` - Auto.dev premium service

**Response:**
```
✅ Decoder service updated to {service}
```

#### Vehicle Actions
**Data:** `vehicle:{vehicle_id}:{action}`

**Actions:**
- `refresh` - Re-decode the VIN
- `save` - Save to user's collection
- `details` - Show extended information
- `share` - Generate shareable link

#### Settings Actions
**Data:** `settings:{category}:{value}`

**Categories:**
- `history_limit` - Set history size (5, 10, 20)
- `auto_save` - Toggle auto-save (on, off)
- `notifications` - Toggle notifications (on, off)

## Web Dashboard REST API

The web dashboard exposes a REST API built with FastAPI for managing vehicles and providing data to the Next.js frontend.

### Base URL
- Development: `http://localhost:5000`
- Production: `https://api.yourdomain.com`

### Authentication
Currently, the API is open for the dashboard. Future versions will implement JWT authentication.

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-12T15:30:00Z"
}
```

#### `GET /api/vehicles`
Retrieve paginated list of decoded vehicles.

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 10): Items per page

**Response:**
```json
{
  "vehicles": [
    {
      "id": 1,
      "vin": "1HGCM82633A004352",
      "manufacturer": "Honda",
      "model": "Accord",
      "year": 2003,
      "vehicle_type": "Sedan",
      "engine_info": "2.4L 4-cylinder",
      "fuel_type": "Gasoline",
      "decoded_at": "2025-01-12T10:30:00Z",
      "user_id": 1,
      "raw_data": {}
    }
  ],
  "total": 150,
  "page": 1,
  "total_pages": 15
}
```

#### `GET /api/vehicles/{vin}`
Retrieve specific vehicle by VIN.

**Path Parameters:**
- `vin` (string): 17-character VIN

**Response:**
```json
{
  "id": 1,
  "vin": "1HGCM82633A004352",
  "manufacturer": "Honda",
  "model": "Accord",
  "year": 2003,
  "vehicle_type": "Sedan",
  "engine_info": "2.4L 4-cylinder",
  "fuel_type": "Gasoline",
  "decoded_at": "2025-01-12T10:30:00Z",
  "user_id": 1,
  "raw_data": {
    "Make": "Honda",
    "Model": "Accord",
    "ModelYear": "2003",
    "PlantCity": "Marysville",
    "PlantCountry": "United States"
  }
}
```

#### `POST /api/decode`
Decode a new VIN.

**Request Body:**
```json
{
  "vin": "1HGCM82633A004352"
}
```

**Response:**
```json
{
  "success": true,
  "vehicle": {
    "id": 1,
    "vin": "1HGCM82633A004352",
    "manufacturer": "Honda",
    "model": "Accord",
    "year": 2003,
    "vehicle_type": "Sedan",
    "engine_info": "2.4L 4-cylinder",
    "fuel_type": "Gasoline",
    "decoded_at": "2025-01-12T10:30:00Z"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid VIN format",
  "message": "VIN must be exactly 17 characters"
}
```

#### `DELETE /api/vehicles/{vehicle_id}`
Delete a vehicle record.

**Path Parameters:**
- `vehicle_id` (integer): Vehicle database ID

**Response:**
```json
{
  "success": true,
  "message": "Vehicle deleted successfully"
}
```

#### `GET /api/stats`
Get dashboard statistics.

**Response:**
```json
{
  "total_vehicles": 150,
  "unique_manufacturers": 23,
  "recent_decodes": 12,
  "popular_manufacturers": [
    {"name": "Honda", "count": 45},
    {"name": "Toyota", "count": 38},
    {"name": "Ford", "count": 27}
  ],
  "decodes_by_day": [
    {"date": "2025-01-12", "count": 12},
    {"date": "2025-01-11", "count": 18},
    {"date": "2025-01-10", "count": 15}
  ]
}
```

### CORS Configuration

The API allows CORS from the following origins:
- `http://localhost:3000` (Next.js development)
- `http://localhost:3001` (Next.js alternative port)
- Production frontend domain

### Error Responses

All error responses follow this format:
```json
{
  "detail": "Error message",
  "status_code": 400,
  "type": "validation_error"
}
```

### Rate Limiting

- **Decode endpoint**: 100 requests per minute per IP
- **Other endpoints**: 1000 requests per minute per IP

### WebSocket Support (Future)

Future versions will support WebSocket connections for real-time updates:
- Live vehicle decode notifications
- Statistics updates
- User activity streams

## Internal Service APIs

### Application Services

#### VehicleApplicationService

##### `decode_vin(vin: str, user_id: str, preference: str) -> VehicleDTO`

Decodes a VIN using the specified decoder service.

**Request:**
```python
result = await vehicle_service.decode_vin(
    vin="1HGCM82633A004352",
    user_id="123456789",
    preference="nhtsa"
)
```

**Response:**
```python
VehicleDTO(
    vin="1HGCM82633A004352",
    make="HONDA",
    model="Accord",
    year=2003,
    body_type="Sedan/Saloon",
    engine=EngineDTO(
        displacement_l=2.4,
        cylinders=4,
        fuel_type="Gasoline"
    ),
    decoded_at="2025-01-11T12:00:00Z",
    source="nhtsa"
)
```

##### `get_vehicle_history(user_id: str, limit: int) -> List[VehicleDTO]`

Retrieves user's VIN decode history.

**Request:**
```python
history = await vehicle_service.get_vehicle_history(
    user_id="123456789",
    limit=10
)
```

**Response:**
```python
[
    VehicleDTO(...),
    VehicleDTO(...),
    ...
]
```

#### UserApplicationService

##### `get_user_preferences(user_id: str) -> UserPreferencesDTO`

Retrieves user preferences.

**Request:**
```python
preferences = await user_service.get_user_preferences(
    user_id="123456789"
)
```

**Response:**
```python
UserPreferencesDTO(
    decoder_service="nhtsa",
    history_limit=10,
    auto_save=False,
    notifications_enabled=True,
    language="en"
)
```

##### `update_user_preferences(user_id: str, preferences: dict) -> None`

Updates user preferences.

**Request:**
```python
await user_service.update_user_preferences(
    user_id="123456789",
    preferences={
        "decoder_service": "autodev",
        "history_limit": 20
    }
)
```

### Command Bus API

#### Command Registration
```python
command_bus.register(DecodeVINCommand, DecodeVINHandler)
command_bus.register(UpdatePreferencesCommand, UpdatePreferencesHandler)
```

#### Command Dispatch
```python
result = await command_bus.dispatch(
    DecodeVINCommand(
        vin=VIN("1HGCM82633A004352"),
        user_id=UserID("123456789"),
        decoder_preference=DecoderPreference.NHTSA
    )
)
```

### Query Bus API

#### Query Registration
```python
query_bus.register(GetVehicleHistoryQuery, GetVehicleHistoryHandler)
query_bus.register(GetUserPreferencesQuery, GetUserPreferencesHandler)
```

#### Query Dispatch
```python
result = await query_bus.dispatch(
    GetVehicleHistoryQuery(
        user_id=UserID("123456789"),
        limit=10
    )
)
```

## External API Integrations

### NHTSA API Integration

#### Base URL
```
https://vpic.nhtsa.dot.gov/api/vehicles
```

#### Decode VIN Endpoint
```http
GET /DecodeVin/{VIN}?format=json
```

**Parameters:**
- `VIN`: 17-character VIN
- `format`: Response format (json)

**Response:**
```json
{
  "Count": 136,
  "Message": "Results returned successfully",
  "SearchCriteria": "VIN:1HGCM82633A004352",
  "Results": [
    {
      "Value": "HONDA",
      "ValueId": "474",
      "Variable": "Make",
      "VariableId": 26
    },
    {
      "Value": "Accord",
      "ValueId": "1861",
      "Variable": "Model",
      "VariableId": 28
    },
    {
      "Value": "2003",
      "ValueId": "",
      "Variable": "Model Year",
      "VariableId": 29
    }
  ]
}
```

#### Rate Limits
- No authentication required
- No official rate limits
- Recommended: 10 requests/second

### Auto.dev API Integration

#### Base URL
```
https://api.auto.dev/v1
```

#### Authentication
```http
Authorization: Bearer {API_KEY}
```

#### Get Vehicle Specs Endpoint
```http
GET /specs?vin={VIN}
```

**Headers:**
```http
Authorization: Bearer your-api-key
Content-Type: application/json
```

**Response:**
```json
{
  "success": true,
  "data": {
    "vin": "1HGCM82633A004352",
    "specs": {
      "make": "Honda",
      "model": "Accord",
      "year": 2003,
      "trim": "EX",
      "msrp": 22750,
      "engine": {
        "type": "2.4L I4",
        "displacement_l": 2.4,
        "cylinders": 4,
        "configuration": "Inline",
        "fuel_type": "Regular Unleaded",
        "horsepower": 160,
        "torque": 161,
        "compression_ratio": "9.7:1"
      },
      "transmission": {
        "type": "5-Speed Automatic",
        "speeds": 5,
        "drivetrain": "FWD"
      },
      "dimensions": {
        "length_in": 189.5,
        "width_in": 71.5,
        "height_in": 57.1,
        "wheelbase_in": 107.9,
        "curb_weight_lbs": 3091
      },
      "fuel_economy": {
        "city_mpg": 21,
        "highway_mpg": 30,
        "combined_mpg": 24
      }
    }
  }
}
```

#### Get Market Value Endpoint
```http
GET /market-value?vin={VIN}&zip={ZIP}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "vin": "1HGCM82633A004352",
    "values": {
      "trade_in": {
        "clean": 4500,
        "average": 3800,
        "rough": 2900
      },
      "private_party": {
        "clean": 5500,
        "average": 4700,
        "rough": 3600
      },
      "dealer_retail": {
        "clean": 6800,
        "average": 5900,
        "rough": 4500
      }
    },
    "confidence": 0.85,
    "data_points": 127,
    "last_updated": "2025-01-11T12:00:00Z"
  }
}
```

#### Get Vehicle History Endpoint
```http
GET /history?vin={VIN}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "vin": "1HGCM82633A004352",
    "owners": 3,
    "accidents": 0,
    "title_status": "Clean",
    "recalls": [
      {
        "campaign_id": "03V417000",
        "description": "Ignition interlock malfunction",
        "remedy": "Replace ignition switch",
        "status": "Incomplete"
      }
    ],
    "service_records": 42,
    "last_odometer": {
      "mileage": 145632,
      "date": "2024-08-15",
      "source": "State Inspection"
    }
  }
}
```

#### Rate Limits
- 1000 requests/day (Free tier)
- 10000 requests/day (Pro tier)
- 100000 requests/day (Enterprise tier)
- Burst: 10 requests/second

## Event APIs

### Domain Events

#### VehicleDecoded Event
```python
@dataclass
class VehicleDecoded(DomainEvent):
    event_id: str
    timestamp: datetime
    vehicle_id: VehicleID
    vin: VIN
    user_id: UserID
    decoder_source: DecoderSource
    success: bool
    
# Publishing
await event_bus.publish(
    VehicleDecoded(
        event_id=str(uuid4()),
        timestamp=datetime.utcnow(),
        vehicle_id=vehicle.id,
        vin=vehicle.vin,
        user_id=user_id,
        decoder_source=DecoderSource.NHTSA,
        success=True
    )
)

# Subscribing
@event_bus.subscribe(VehicleDecoded)
async def handle_vehicle_decoded(event: VehicleDecoded):
    # Update user history
    # Send analytics
    # Clear cache
    pass
```

#### UserPreferencesUpdated Event
```python
@dataclass
class UserPreferencesUpdated(DomainEvent):
    event_id: str
    timestamp: datetime
    user_id: UserID
    changes: Dict[str, Any]
    
# Publishing
await event_bus.publish(
    UserPreferencesUpdated(
        event_id=str(uuid4()),
        timestamp=datetime.utcnow(),
        user_id=user_id,
        changes={"decoder_service": "autodev"}
    )
)
```

### Event Bus Interface

#### Subscribe to Events
```python
class EventHandler:
    @event_bus.subscribe(VehicleDecoded)
    async def on_vehicle_decoded(self, event: VehicleDecoded):
        logger.info(f"Vehicle decoded: {event.vin}")
    
    @event_bus.subscribe(UserPreferencesUpdated)
    async def on_preferences_updated(self, event: UserPreferencesUpdated):
        await self.cache.invalidate(f"user:{event.user_id}")
```

#### Publish Events
```python
async def publish_event(event: DomainEvent):
    await event_bus.publish(event)
    
    # With error handling
    try:
        await event_bus.publish(event)
    except EventPublishError as e:
        logger.error(f"Failed to publish event: {e}")
        # Implement retry or dead letter queue
```

## Error Codes

### Application Error Codes

| Code | Description | HTTP Status | User Message |
|------|-------------|-------------|--------------|
| `INVALID_VIN` | VIN format validation failed | 400 | "Invalid VIN format. Please check and try again." |
| `VIN_NOT_FOUND` | VIN not found in database | 404 | "Vehicle information not found for this VIN." |
| `DECODER_UNAVAILABLE` | External decoder service down | 503 | "Service temporarily unavailable. Please try again later." |
| `RATE_LIMITED` | Rate limit exceeded | 429 | "Too many requests. Please wait {seconds} seconds." |
| `INVALID_PREFERENCE` | Invalid user preference value | 400 | "Invalid preference value." |
| `USER_NOT_FOUND` | User not registered | 404 | "Please use /start to register first." |
| `CACHE_ERROR` | Cache operation failed | 500 | "Temporary issue. Please try again." |
| `DATABASE_ERROR` | Database operation failed | 500 | "System error. Please try again later." |
| `EXTERNAL_API_ERROR` | External API call failed | 502 | "External service error. Please try again." |
| `VALIDATION_ERROR` | Input validation failed | 400 | "Invalid input. Please check and try again." |

### External API Error Handling

#### NHTSA Errors
```python
class NHTSAErrorHandler:
    def handle_response(self, response: dict) -> VehicleInfo:
        if response.get("Count") == 0:
            raise VINNotFoundError("No results from NHTSA")
        
        if "Error" in response.get("Message", ""):
            raise ExternalAPIError(response["Message"])
        
        return self.transform_response(response)
```

#### Auto.dev Errors
```python
class AutoDevErrorHandler:
    ERROR_CODES = {
        "INVALID_API_KEY": InvalidAPIKeyError,
        "RATE_LIMIT_EXCEEDED": RateLimitError,
        "VIN_NOT_FOUND": VINNotFoundError,
        "INTERNAL_ERROR": ExternalAPIError
    }
    
    def handle_response(self, response: dict) -> VehicleInfo:
        if not response.get("success"):
            error_code = response.get("error", {}).get("code")
            error_class = self.ERROR_CODES.get(
                error_code, ExternalAPIError
            )
            raise error_class(response.get("error", {}).get("message"))
        
        return self.transform_response(response["data"])
```

## Rate Limiting

### User Rate Limits

```python
class RateLimiter:
    LIMITS = {
        "decode_vin": {"requests": 30, "window": 60},  # 30/minute
        "get_history": {"requests": 10, "window": 60},  # 10/minute
        "update_preferences": {"requests": 5, "window": 60},  # 5/minute
    }
    
    async def check_rate_limit(
        self,
        user_id: str,
        action: str
    ) -> bool:
        key = f"rate_limit:{user_id}:{action}"
        current = await self.cache.increment(key)
        
        if current == 1:
            # First request, set expiry
            await self.cache.expire(key, self.LIMITS[action]["window"])
        
        if current > self.LIMITS[action]["requests"]:
            ttl = await self.cache.ttl(key)
            raise RateLimitError(
                f"Rate limit exceeded for {action}",
                retry_after=ttl
            )
        
        return True
```

### API Rate Limit Headers

```python
class RateLimitMiddleware:
    async def process_response(self, response: Response, context: dict):
        response.headers["X-RateLimit-Limit"] = str(context["limit"])
        response.headers["X-RateLimit-Remaining"] = str(context["remaining"])
        response.headers["X-RateLimit-Reset"] = str(context["reset"])
        
        if context["remaining"] == 0:
            response.headers["Retry-After"] = str(context["retry_after"])
```

## Future REST API

### Planned Endpoints

#### Authentication
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

#### VIN Operations
```http
GET /api/v1/vin/{vin}
POST /api/v1/vin/decode
POST /api/v1/vin/batch
GET /api/v1/vin/{vin}/history
GET /api/v1/vin/{vin}/market-value
GET /api/v1/vin/{vin}/recalls
```

#### User Management
```http
GET /api/v1/user/profile
PUT /api/v1/user/profile
GET /api/v1/user/preferences
PUT /api/v1/user/preferences
GET /api/v1/user/history
DELETE /api/v1/user/history
GET /api/v1/user/saved
POST /api/v1/user/saved
DELETE /api/v1/user/saved/{id}
```

#### Webhooks
```http
POST /api/v1/webhooks
GET /api/v1/webhooks
PUT /api/v1/webhooks/{id}
DELETE /api/v1/webhooks/{id}
POST /api/v1/webhooks/{id}/test
```

### OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: VIN Decoder API
  version: 1.0.0
  description: RESTful API for VIN decoding services

servers:
  - url: https://api.vindecoder.example.com/v1
    description: Production server
  - url: https://staging-api.vindecoder.example.com/v1
    description: Staging server

paths:
  /vin/{vin}:
    get:
      summary: Decode a VIN
      parameters:
        - name: vin
          in: path
          required: true
          schema:
            type: string
            pattern: '^[A-HJ-NPR-Z0-9]{17}$'
      responses:
        200:
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Vehicle'
        400:
          $ref: '#/components/responses/BadRequest'
        404:
          $ref: '#/components/responses/NotFound'
        429:
          $ref: '#/components/responses/RateLimited'

components:
  schemas:
    Vehicle:
      type: object
      properties:
        vin:
          type: string
        make:
          type: string
        model:
          type: string
        year:
          type: integer
        engine:
          $ref: '#/components/schemas/Engine'
    
    Engine:
      type: object
      properties:
        displacement_l:
          type: number
        cylinders:
          type: integer
        fuel_type:
          type: string
  
  responses:
    BadRequest:
      description: Bad request
    NotFound:
      description: Resource not found
    RateLimited:
      description: Rate limit exceeded
```

### SDK Examples

#### Python SDK
```python
from vindecoder import VINDecoderClient

client = VINDecoderClient(api_key="your-api-key")

# Decode a VIN
vehicle = await client.decode_vin("1HGCM82633A004352")
print(f"{vehicle.year} {vehicle.make} {vehicle.model}")

# Get market value
value = await client.get_market_value("1HGCM82633A004352", zip_code="10001")
print(f"Trade-in value: ${value.trade_in.average}")

# Batch decode
vehicles = await client.batch_decode([
    "1HGCM82633A004352",
    "WBA3B5C50FF970265",
    "JH4KA7650PC003452"
])
```

#### JavaScript SDK
```javascript
import { VINDecoderClient } from '@vindecoder/sdk';

const client = new VINDecoderClient({ apiKey: 'your-api-key' });

// Decode a VIN
const vehicle = await client.decodeVIN('1HGCM82633A004352');
console.log(`${vehicle.year} ${vehicle.make} ${vehicle.model}`);

// Subscribe to webhooks
client.webhooks.subscribe('vehicle.decoded', async (event) => {
  console.log(`VIN decoded: ${event.vin}`);
});
```

## Testing

### API Testing with pytest

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_decode_vin():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/vin/1HGCM82633A004352")
        assert response.status_code == 200
        data = response.json()
        assert data["vin"] == "1HGCM82633A004352"
        assert data["make"] == "HONDA"
        assert data["model"] == "Accord"
        assert data["year"] == 2003
```

### Load Testing with Locust

```python
from locust import HttpUser, task, between

class VINDecoderUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(weight=3)
    def decode_vin(self):
        self.client.get("/api/v1/vin/1HGCM82633A004352")
    
    @task(weight=1)
    def get_history(self):
        self.client.get("/api/v1/user/history")
    
    def on_start(self):
        # Authenticate
        self.client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
```

---

*Last Updated: January 2025*  
*Version: 1.0.0*