from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

app = FastAPI(title="VIN Decoder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VINRequest(BaseModel):
    vin: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/vehicles")
async def get_vehicles(page: int = 1, limit: int = 10):
    """Return mock vehicle data"""
    mock_vehicles = [
        {
            "id": 1,
            "vin": "1HGBH41JXMN109186",
            "manufacturer": "Honda",
            "model": "Civic",
            "year": 2023,
            "vehicle_type": "Sedan",
            "engine_info": "2.0L 4-Cylinder",
            "fuel_type": "Gasoline",
            "decoded_at": datetime.utcnow().isoformat(),
            "user_id": 1,
            "raw_data": {}
        },
        {
            "id": 2,
            "vin": "5YJ3E1EA1JF00001",
            "manufacturer": "Tesla",
            "model": "Model 3",
            "year": 2023,
            "vehicle_type": "Sedan",
            "engine_info": "Electric Motor",
            "fuel_type": "Electric",
            "decoded_at": datetime.utcnow().isoformat(),
            "user_id": 1,
            "raw_data": {}
        }
    ]
    
    offset = (page - 1) * limit
    return {
        "vehicles": mock_vehicles[offset:offset + limit],
        "total_pages": 1
    }

@app.get("/api/stats")
async def get_stats():
    """Return mock statistics"""
    return {
        "total_vehicles": 2,
        "unique_manufacturers": 2,
        "recent_decodes": 2
    }

@app.post("/api/decode")
async def decode_vin(request: VINRequest):
    """Mock VIN decoding"""
    if len(request.vin) != 17:
        raise HTTPException(status_code=400, detail="VIN must be exactly 17 characters")
    
    return {
        "success": True,
        "vehicle": {
            "id": 3,
            "vin": request.vin.upper(),
            "manufacturer": "Mock Manufacturer",
            "model": "Mock Model",
            "year": 2023,
            "vehicle_type": "Sedan",
            "engine_info": "Mock Engine",
            "fuel_type": "Gasoline",
            "decoded_at": datetime.utcnow().isoformat(),
            "user_id": 1,
            "raw_data": {"mock": True}
        }
    }

@app.delete("/api/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: int):
    """Mock vehicle deletion"""
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)