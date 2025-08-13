# IntelAuto Vehicle Intelligence API Documentation

## 📚 Related Documentation
- **[📖 Main README](../../README.md)** - Platform overview and complete setup guide
- **[🏗️ Architecture Guide](../technical/architecture.md)** - Complete system architecture and design patterns
- **[📋 Documentation Hub](../README.md)** - Complete documentation index
- **[🌐 Dashboard Guide](../user-guides/web-dashboard.md)** - Next.js web dashboard setup and usage
- **[🔌 Integrations Guide](../integrations/README.md)** - Data sources and third-party integrations
- **[🚀 Development Roadmap](../business/roadmap.md)** - Strategic technology roadmap

Welcome to the IntelAuto API documentation. This REST API provides comprehensive vehicle intelligence including VIN decoding, specifications, and vehicle management capabilities powered by **NHTSA** and **Auto.dev** integrations.

## Table of Contents

- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
- [Response Models](#response-models)
- [Usage Examples](#usage-examples)
- [Interactive Documentation](#interactive-documentation)

---

## Authentication

### JWT Bearer Tokens

The IntelAuto API uses JWT (JSON Web Token) authentication. All requests must include a valid JWT token in the Authorization header.

**Authentication Method**: Bearer Token
- **Header**: `Authorization: Bearer <JWT_TOKEN>`
- **Type**: `string`
- **Required**: Yes (for protected endpoints)

**Getting Your JWT Token**:
1. Register at [IntelAuto Dashboard](https://dashboard.intellauto.com) *(coming soon)*
2. Navigate to Settings » API Keys
3. Generate a new API key
4. Use the API key to obtain JWT tokens through the `/auth/login` endpoint

**Security Best Practices**:
- Store JWT tokens securely and never expose them in client-side code
- JWT tokens expire after 24 hours by default
- Use environment variables to store your credentials
- Monitor your API usage in the dashboard

---

## Rate Limiting

The API implements rate limiting to ensure fair usage and optimal performance for all users.

**Rate Limits by Tier**:
- **Free**: 100 VIN decodes per month
- **Professional**: 2,500 VIN decodes per month
- **Enterprise**: 10,000 VIN decodes per month
- **Custom**: Unlimited or custom limits

**Headers Returned**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

**Rate Limit Exceeded Response**:
```json
{
  "detail": "Rate limit exceeded. Please upgrade your plan or wait before making additional requests."
}
```

---

## Error Handling

### Error Response Format

All API errors follow FastAPI's standard format:

```json
{
  "detail": "Human-readable error description"
}
```

### Common HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid VIN format or missing parameters |
| `401` | Unauthorized - Invalid or missing JWT token |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Vehicle not found or endpoint doesn't exist |
| `429` | Too Many Requests - Rate limit exceeded |
| `500` | Internal Server Error |

---

## API Endpoints

### GET /health

Health check endpoint to verify API status.

**Authentication**: None required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-04-02T22:21:33.819Z",
  "database": "healthy",
  "cache": "healthy"
}
```

### POST /api/decode

Decode a single VIN using the domain service.

**Authentication**: Optional (better results when authenticated)

**Request Body**:
```json
{
  "vin": "1HGBH41JXMN109186",
  "force_refresh": false,
  "preferred_service": "autodev"
}
```

**Parameters**:
- `vin` (required): 17-character Vehicle Identification Number
- `force_refresh` (optional): Force fresh decode even if cached (default: false)
- `preferred_service` (optional): Preferred decoder service - "nhtsa" or "autodev" (default: "autodev")

**Response**:
```json
{
  "success": true,
  "vehicle": {
    "id": "123",
    "vin": "1HGBH41JXMN109186",
    "manufacturer": "Honda",
    "model": "Civic",
    "year": 2023,
    "vehicle_type": "PASSENGER CAR",
    "engine_info": "1.5L L4 DOHC 16V",
    "fuel_type": "Gasoline",
    "decoded_at": "2024-04-02T22:21:33.819Z",
    "user_id": null,
    "raw_data": {
      "nhtsa_data": {...},
      "autodev_data": {...}
    }
  }
}
```

### GET /api/vehicles

Get paginated list of decoded vehicles.

**Authentication**: None required (returns all vehicles)

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)

**Response**:
```json
{
  "vehicles": [
    {
      "id": "123",
      "vin": "1HGBH41JXMN109186",
      "manufacturer": "Honda",
      "model": "Civic",
      "year": 2023,
      "vehicle_type": "PASSENGER CAR",
      "engine_info": "1.5L L4 DOHC 16V",
      "fuel_type": "Gasoline",
      "decoded_at": "2024-04-02T22:21:33.819Z",
      "user_id": null,
      "raw_data": {}
    }
  ],
  "page": 1,
  "limit": 10,
  "total": 1,
  "total_pages": 1
}
```

### GET /api/stats

Get application statistics.

**Authentication**: None required

**Response**:
```json
{
  "total_vehicles": 150,
  "unique_manufacturers": 25,
  "recent_decodes": 10
}
```

### DELETE /api/vehicles/{vehicle_id}

Delete a vehicle by ID.

**Authentication**: None required

**Parameters**:
- `vehicle_id` (path, required): Vehicle ID to delete

**Response**:
```json
{
  "success": true
}
```

### GET /api/users/me

Get current user information (mock endpoint).

**Authentication**: None required

**Response**:
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "demo_user",
  "first_name": "Demo",
  "last_name": "User",
  "preferences": {
    "preferred_service": "autodev",
    "language_code": "en"
  }
}
```

---

## Data Sources

### Current Integrations

#### NHTSA (National Highway Traffic Safety Administration)
- **Type**: Government vehicle safety database
- **Coverage**: All US market vehicles 1981+
- **Data**: Basic specifications, safety ratings, recall information
- **Cost**: Free API access
- **Reliability**: 99.9% uptime, official government data

#### Auto.dev API
- **Type**: Comprehensive automotive data platform
- **Coverage**: Global vehicle database with enhanced specifications
- **Data**: Detailed specifications, trim information, option packages
- **Cost**: API key required, usage-based pricing
- **Features**: Premium vehicle data, international VIN support

### Service Selection

The API automatically selects the best data source:
1. **Auto.dev** is used as the primary service (when API key is configured)
2. **NHTSA** is used as fallback when Auto.dev is unavailable
3. Users can specify `preferred_service` in requests

---

## Response Models

### Vehicle Response Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique vehicle identifier |
| `vin` | string | 17-character Vehicle Identification Number |
| `manufacturer` | string | Vehicle manufacturer (e.g., "Honda", "BMW") |
| `model` | string | Vehicle model name |
| `year` | integer | Manufacturing year |
| `vehicle_type` | string | Vehicle type/body style |
| `engine_info` | string | Engine specification |
| `fuel_type` | string | Fuel type (Gasoline, Diesel, Electric, etc.) |
| `decoded_at` | string | ISO timestamp when vehicle was decoded |
| `user_id` | integer/null | Associated user ID (if applicable) |
| `raw_data` | object | Raw response data from data sources |

---

## Usage Examples

### Basic VIN Decoding with cURL

```bash
# Decode a single VIN
curl -X POST "http://localhost:5000/api/decode" \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "1HGBH41JXMN109186",
    "preferred_service": "autodev"
  }'
```

### VIN Decoding with Force Refresh

```bash
# Force fresh decode bypassing cache
curl -X POST "http://localhost:5000/api/decode" \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "1HGBH41JXMN109186",
    "force_refresh": true
  }'
```

### Get All Vehicles

```bash
# Get paginated vehicle list
curl "http://localhost:5000/api/vehicles?page=1&limit=20"
```

### Python Example

```python
import requests
import json

BASE_URL = "http://localhost:5000"  # or your deployed API URL

def decode_vin(vin, preferred_service="autodev", force_refresh=False):
    """Decode a VIN using the IntelAuto API"""
    url = f"{BASE_URL}/api/decode"
    
    payload = {
        "vin": vin,
        "preferred_service": preferred_service,
        "force_refresh": force_refresh
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_vehicles(page=1, limit=10):
    """Get paginated list of vehicles"""
    url = f"{BASE_URL}/api/vehicles"
    params = {"page": page, "limit": limit}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Example usage
if __name__ == "__main__":
    # Decode a VIN
    vin = "1HGBH41JXMN109186"
    result = decode_vin(vin)
    
    if result and result.get("success"):
        vehicle = result["vehicle"]
        print(f"Vehicle: {vehicle['year']} {vehicle['manufacturer']} {vehicle['model']}")
        print(f"Engine: {vehicle['engine_info']}")
        print(f"Fuel Type: {vehicle['fuel_type']}")
    
    # Get vehicles list
    vehicles = get_vehicles(page=1, limit=5)
    if vehicles:
        print(f"\nFound {vehicles['total']} vehicles:")
        for vehicle in vehicles['vehicles']:
            print(f"- {vehicle['year']} {vehicle['manufacturer']} {vehicle['model']}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000'; // or your deployed API URL

async function decodeVIN(vin, options = {}) {
    try {
        const payload = {
            vin: vin,
            preferred_service: options.preferredService || 'autodev',
            force_refresh: options.forceRefresh || false
        };

        const response = await axios.post(`${BASE_URL}/api/decode`, payload, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        return response.data;
    } catch (error) {
        console.error('Error decoding VIN:', error.response?.data || error.message);
        return null;
    }
}

async function getVehicles(page = 1, limit = 10) {
    try {
        const response = await axios.get(`${BASE_URL}/api/vehicles`, {
            params: { page, limit }
        });
        
        return response.data;
    } catch (error) {
        console.error('Error getting vehicles:', error.response?.data || error.message);
        return null;
    }
}

// Example usage
async function example() {
    // Decode a VIN
    const vin = '1HGBH41JXMN109186';
    const result = await decodeVIN(vin, { preferredService: 'autodev' });
    
    if (result && result.success) {
        const vehicle = result.vehicle;
        console.log(`Vehicle: ${vehicle.year} ${vehicle.manufacturer} ${vehicle.model}`);
        console.log(`Engine: ${vehicle.engine_info}`);
        console.log(`Fuel Type: ${vehicle.fuel_type}`);
    }
    
    // Get vehicles list
    const vehicles = await getVehicles(1, 5);
    if (vehicles) {
        console.log(`\nFound ${vehicles.total} vehicles:`);
        vehicles.vehicles.forEach(vehicle => {
            console.log(`- ${vehicle.year} ${vehicle.manufacturer} ${vehicle.model}`);
        });
    }
}

example();
```

---

## Interactive Documentation

For interactive API testing and comprehensive endpoint documentation, visit the **FastAPI Swagger UI**:

🔗 **[http://localhost:5000/docs](http://localhost:5000/docs)** (local development)
🔗 **[https://api.intellauto.com/docs](https://api.intellauto.com/docs)** *(coming soon)*

The Swagger UI provides:
- Interactive API testing interface
- Complete request/response schemas
- Real-time API responses
- Automatic code generation
- Comprehensive parameter documentation

### Alternative Documentation

- **ReDoc**: [http://localhost:5000/redoc](http://localhost:5000/redoc)
- **OpenAPI JSON**: [http://localhost:5000/openapi.json](http://localhost:5000/openapi.json)

### Additional Resources

- **GitHub Repository**: [https://github.com/lucchesi-sec/telegram-vin-decoder-bot](https://github.com/lucchesi-sec/telegram-vin-decoder-bot)
- **Issues & Support**: [GitHub Issues](https://github.com/lucchesi-sec/telegram-vin-decoder-bot/issues)
- **Community**: [GitHub Discussions](https://github.com/lucchesi-sec/telegram-vin-decoder-bot/discussions)

---

## API Versioning

**Current Version**: `2.0.0`

The IntelAuto API follows semantic versioning. Major version changes may introduce breaking changes, while minor and patch versions maintain backward compatibility.

---

*Last updated: January 2025*
