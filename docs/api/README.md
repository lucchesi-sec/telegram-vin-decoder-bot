# CarsXE Vehicle Intelligence API Documentation

## 📚 Related Documentation
- **[📖 Main README](../../README.md)** - Platform overview and complete setup guide
- **[🏗️ Architecture Guide](../../ARCHITECTURE.md)** - Complete system architecture and design patterns
- **[📋 Documentation Hub](../README.md)** - Complete documentation index
- **[📦 Dashboard Guide](../../README_DASHBOARD.md)** - Next.js web dashboard setup and usage
- **[🔌 Integrations Guide](../integrations/README.md)** - Data sources and third-party integrations
- **[🚀 Development Roadmap](../../FUTURE_PLANS.md)** - Strategic technology roadmap

Welcome to the CarsXE API documentation. This API provides comprehensive vehicle data including VIN decoding, specifications, market values, and batch processing capabilities.

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

### API Key Management

The CarsXE API uses API key authentication. All requests must include your API key as a query parameter.

**Authentication Method**: Query Parameter
- **Parameter**: `key`
- **Type**: `string`
- **Required**: Yes

**Getting Your API Key**:
1. Register at [CarsXE Dashboard](https://api.carsxe.com/dashboard)
2. Navigate to Dashboard » Profile
3. Copy your API key

**Security Best Practices**:
- Keep your API key secure and never expose it in client-side code
- Use environment variables to store your API key
- Rotate your API key regularly
- Monitor your API usage in the dashboard

---

## Rate Limiting

The API implements rate limiting to ensure fair usage and optimal performance for all users.

**Rate Limits**:
- Free tier: 100 requests per day
- Paid plans: Varies by subscription level

**Headers Returned**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

**Rate Limit Exceeded Response**:
```json
{
  "success": false,
  "error": "rate_limit_exceeded",
  "message": "API rate limit exceeded. Please upgrade your plan or wait before making additional requests."
}
```

---

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable error description",
  "timestamp": "2024-04-02T22:21:33.819Z"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `invalid_inputs` | 400 | Missing required parameters (VIN, key, etc.) |
| `invalid_vin` | 400 | VIN format is invalid or not 17 characters |
| `no_data` | 404 | No vehicle data found for the provided VIN |
| `api_not_enabled` | 403 | API endpoint not enabled for your subscription |
| `rate_limit_exceeded` | 429 | API rate limit exceeded |
| `invalid_api_key` | 401 | API key is invalid or expired |
| `server_error` | 500 | Internal server error occurred |

---

## API Endpoints

### GET /api/v1/vin/decode/:vin

Decode a single VIN to retrieve comprehensive vehicle specifications.

**Parameters**:
- `vin` (path, required): 17-character Vehicle Identification Number
- `key` (query, required): Your API key
- `format` (query, optional): Response format (`json` or `xml`, defaults to `json`)
- `deepdata` (query, optional): Set to `1` for additional deep data (slower response)
- `disableIntVINDecoding` (query, optional): Set to `1` to disable international VIN fallback

**Example Request**:
```bash
GET /api/v1/vin/decode/WBAFR7C57CC811956?key=YOUR_API_KEY
```

### POST /api/v1/batch/decode

Decode multiple VINs in a single request for improved efficiency.

**Request Body**:
```json
{
  "vins": ["WBAFR7C57CC811956", "WF0MXXGBWM8R43240"],
  "options": {
    "deepdata": false,
    "disableIntVINDecoding": false
  }
}
```

**Parameters**:
- `key` (query, required): Your API key
- `vins` (body, required): Array of VINs to decode (max 100)
- `options` (body, optional): Processing options

### GET /api/v1/vehicles

List and filter vehicles based on various criteria.

**Query Parameters**:
- `key` (required): Your API key
- `make` (optional): Filter by manufacturer
- `model` (optional): Filter by model
- `year` (optional): Filter by year
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Pagination offset

**Example Request**:
```bash
GET /api/v1/vehicles?key=YOUR_API_KEY&make=BMW&year=2012&limit=20
```

### GET /api/v1/vehicles/:id

Get detailed information for a specific vehicle by ID.

**Parameters**:
- `id` (path, required): Vehicle ID
- `key` (query, required): Your API key
- `include_specs` (query, optional): Include full specifications
- `include_colors` (query, optional): Include available colors
- `include_equipment` (query, optional): Include equipment details

### GET /api/v1/stats

Retrieve API usage statistics and account information.

**Parameters**:
- `key` (query, required): Your API key
- `period` (query, optional): Time period for stats (`day`, `week`, `month`)

**Response**:
```json
{
  "success": true,
  "data": {
    "requests_today": 45,
    "requests_this_month": 1250,
    "plan": "Professional",
    "rate_limit": 10000,
    "remaining_requests": 8750
  },
  "timestamp": "2024-04-02T22:21:33.819Z"
}
```

---

## Response Models

### Vehicle Specifications Response

```json
{
  "success": true,
  "input": {
    "key": "API_KEY",
    "vin": "WBAFR7C57CC811956"
  },
  "attributes": {
    "year": "2012",
    "make": "BMW",
    "model": "5-Series",
    "trim": "535i",
    "style": "SEDAN 4-DR",
    "made_in": "GERMANY",
    "fuel_capacity": "18.50 gallon",
    "city_mileage": "19 - 21 miles/gallon",
    "highway_mileage": "29 - 31 miles/gallon",
    "engine": "3.0L L6 DOHC 24V",
    "transmission": "6-Speed Manual | 8-Speed Automatic",
    "drivetrain": "RWD",
    "curb_weight": "4090 lbs",
    "overall_height": "57.60 in.",
    "overall_length": "193.10 in.",
    "overall_width": "73.20 in.",
    "wheelbase_length": "116.90 in.",
    "standard_seating": "5",
    "manufacturer_suggested_retail_price": "$52,500 USD"
  },
  "colors": [
    {
      "category": "Exterior",
      "name": "Alpine White"
    },
    {
      "category": "Interior",
      "name": "Black Dakota Leather Interior"
    }
  ],
  "equipment": {
    "abs_brakes": "Std.",
    "air_conditioning": "Std.",
    "leather_seat": "Std.",
    "navigation_aid": "Opt."
  },
  "warranties": [
    {
      "type": "Basic",
      "miles": "50,000 mile",
      "months": "48 month"
    }
  ],
  "timestamp": "2024-04-02T22:21:33.819Z"
}
```

### Field Definitions for Vehicle Intelligence

| Field | Type | Description |
|-------|------|-------------|
| `year` | string | Manufacturing year |
| `make` | string | Vehicle manufacturer (e.g., "BMW", "Ford") |
| `model` | string | Vehicle model name |
| `trim` | string | Trim level or variant |
| `style` | string | Body style (e.g., "SEDAN 4-DR") |
| `made_in` | string | Country of manufacture |
| `fuel_type` | string | Type of fuel (Gas, Diesel, Electric, Hybrid) |
| `fuel_capacity` | string | Fuel tank capacity |
| `city_mileage` | string | EPA city fuel economy rating |
| `highway_mileage` | string | EPA highway fuel economy rating |
| `engine` | string | Engine specification |
| `transmission` | string | Transmission type and speeds |
| `drivetrain` | string | Drive configuration (RWD, FWD, AWD, 4WD) |
| `curb_weight` | string | Vehicle weight without cargo/passengers |
| `overall_height` | string | Total vehicle height |
| `overall_length` | string | Total vehicle length |
| `overall_width` | string | Total vehicle width |
| `wheelbase_length` | string | Distance between front and rear axles |
| `standard_seating` | string | Number of standard seats |
| `manufacturer_suggested_retail_price` | string | MSRP when new |

### International VIN Decoder Response

```json
{
  "success": true,
  "input": {
    "vin": "WF0MXXGBWM8R43240"
  },
  "attributes": {
    "vin": "WF0MXXGBWM8R43240",
    "make": "Ford",
    "model": "Galaxy",
    "year": "2008",
    "product_type": "Car",
    "body": "Wagon",
    "fuel_type": "Diesel",
    "manufacturer": "FORD-WERKE GmbH, D-50735 KOELN",
    "plant_country": "Germany",
    "avg_co2_emission_g_km": "174.03",
    "no_of_doors": "4",
    "no_of_seats": "5-7",
    "weight_empty_kg": "1806",
    "max_weight_kg": "2505"
  },
  "timestamp": "2025-04-11T00:05:36.457Z"
}
```

---

## Usage Examples

### Basic VIN Decoding with cURL

```bash
# Decode a single VIN
curl -G https://api.carsxe.com/specs \
  -d key=YOUR_API_KEY \
  -d vin=WBAFR7C57CC811956
```

### VIN Decoding with Deep Data

```bash
# Get comprehensive vehicle data (slower response)
curl -G https://api.carsxe.com/specs \
  -d key=YOUR_API_KEY \
  -d vin=WBAFR7C57CC811956 \
  -d deepdata=1
```

### Batch VIN Decoding

```bash
# Decode multiple VINs in one request
curl -X POST https://api.carsxe.com/v1/batch/decode \
  -H "Content-Type: application/json" \
  -d '{
    "key": "YOUR_API_KEY",
    "vins": ["WBAFR7C57CC811956", "WF0MXXGBWM8R43240"],
    "options": {
      "deepdata": false
    }
  }'
```

### Vehicle Search

```bash
# Search for BMW vehicles from 2012
curl -G https://api.carsxe.com/v1/vehicles \
  -d key=YOUR_API_KEY \
  -d make=BMW \
  -d year=2012 \
  -d limit=10
```

### Python Example

```python
import requests
import os

# Set your API key as an environment variable
API_KEY = os.environ.get('CARSXE_API_KEY')
BASE_URL = 'https://api.carsxe.com'

def decode_vin(vin, deep_data=False):
    """Decode a VIN using the CarsXE API"""
    params = {
        'key': API_KEY,
        'vin': vin
    }
    
    if deep_data:
        params['deepdata'] = '1'
    
    response = requests.get(f'{BASE_URL}/specs', params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Example usage
if __name__ == "__main__":
    vin = "WBAFR7C57CC811956"
    result = decode_vin(vin, deep_data=True)
    
    if result and result.get('success'):
        vehicle = result['attributes']
        print(f"Vehicle: {vehicle['year']} {vehicle['make']} {vehicle['model']}")
        print(f"Engine: {vehicle['engine']}")
        print(f"MSRP: {vehicle['manufacturer_suggested_retail_price']}")
    else:
        print("Failed to decode VIN")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const API_KEY = process.env.CARSXE_API_KEY;
const BASE_URL = 'https://api.carsxe.com';

async function decodeVIN(vin, options = {}) {
    try {
        const params = {
            key: API_KEY,
            vin: vin,
            ...options
        };

        const response = await axios.get(`${BASE_URL}/specs`, { params });
        
        if (response.data.success) {
            return response.data;
        } else {
            throw new Error(`API Error: ${response.data.error}`);
        }
    } catch (error) {
        console.error('Error decoding VIN:', error.message);
        return null;
    }
}

// Example usage
async function example() {
    const vin = 'WBAFR7C57CC811956';
    const result = await decodeVIN(vin, { deepdata: '1' });
    
    if (result) {
        const vehicle = result.attributes;
        console.log(`Vehicle: ${vehicle.year} ${vehicle.make} ${vehicle.model}`);
        console.log(`Engine: ${vehicle.engine}`);
        console.log(`MSRP: ${vehicle.manufacturer_suggested_retail_price}`);
    }
}

example();
```

### PHP Example

```php
<?php

class CarsXEAPI {
    private $apiKey;
    private $baseUrl = 'https://api.carsxe.com';
    
    public function __construct($apiKey) {
        $this->apiKey = $apiKey;
    }
    
    public function decodeVIN($vin, $options = []) {
        $params = array_merge([
            'key' => $this->apiKey,
            'vin' => $vin
        ], $options);
        
        $url = $this->baseUrl . '/specs?' . http_build_query($params);
        
        $response = file_get_contents($url);
        
        if ($response === FALSE) {
            return null;
        }
        
        return json_decode($response, true);
    }
}

// Example usage
$api = new CarsXEAPI($_ENV['CARSXE_API_KEY']);
$result = $api->decodeVIN('WBAFR7C57CC811956', ['deepdata' => '1']);

if ($result && $result['success']) {
    $vehicle = $result['attributes'];
    echo "Vehicle: {$vehicle['year']} {$vehicle['make']} {$vehicle['model']}\n";
    echo "Engine: {$vehicle['engine']}\n";
    echo "MSRP: {$vehicle['manufacturer_suggested_retail_price']}\n";
}
?>
```

---

## Interactive Documentation

For interactive API testing and comprehensive endpoint documentation, visit our **FastAPI Swagger UI**:

🔗 **[https://api.carsxe.com/docs](https://api.carsxe.com/docs)**

The Swagger UI provides:
- Interactive API testing interface
- Complete request/response schemas
- Authentication testing
- Real-time API responses
- Code generation in multiple languages
- Comprehensive parameter documentation

### Additional Resources

- **Dashboard**: [https://api.carsxe.com/dashboard](https://api.carsxe.com/dashboard)
- **Support**: Contact our support team for technical assistance
- **Status Page**: Monitor API uptime and performance
- **Changelog**: Stay updated with API changes and improvements

---

*Last updated: 2024-04-02*
