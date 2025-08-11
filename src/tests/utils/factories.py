"""Test factories and builders for creating test data."""

from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import uuid4
import random
import string

from src.domain.user.entities.user import User
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.domain.vehicle.entities.vehicle import Vehicle
from src.domain.vehicle.value_objects.vin_number import VINNumber
from src.domain.vehicle.value_objects.model_year import ModelYear
from src.domain.vehicle.value_objects.decode_result import DecodeResult


class VINFactory:
    """Factory for creating VIN numbers and related data."""
    
    # Valid VIN patterns from different manufacturers
    VIN_PATTERNS = [
        "1HGBH41JXMN{:06d}",  # Honda Civic
        "WBANE53517C{:06d}",  # BMW 5 Series
        "1FTFW1ET5DF{:06d}",  # Ford F-150
        "2T1BURHE0FC{:06d}",  # Toyota Corolla
        "5YJSA1DN5DF{:06d}",  # Tesla Model S
        "WP0AA2A92GS{:06d}",  # Porsche 911
        "JHMCM56557C{:06d}",  # Honda Accord
        "1G1YY26E785{:06d}",  # Chevrolet Corvette
        "KMHDU4AD1AU{:06d}",  # Hyundai Elantra
        "JN1CV6AP9CM{:06d}",  # Nissan Altima
    ]
    
    @classmethod
    def create_valid_vin(cls, pattern_index: int = 0) -> str:
        """Create a valid VIN number."""
        pattern = cls.VIN_PATTERNS[pattern_index % len(cls.VIN_PATTERNS)]
        return pattern.format(random.randint(100000, 999999))
    
    @classmethod
    def create_invalid_vin(cls) -> str:
        """Create an invalid VIN number."""
        invalid_patterns = [
            "ABC123",  # Too short
            "INVALIDVIN12345678",  # Too long
            "12345678901234567",  # Numbers only
            "ABCDEFGHIJKLMNOPQ",  # Letters only
            "1234567890ABCDEFG",  # Correct length but invalid format
        ]
        return random.choice(invalid_patterns)
    
    @classmethod
    def create_vin_batch(cls, count: int = 5, valid: bool = True) -> List[str]:
        """Create a batch of VIN numbers."""
        if valid:
            return [cls.create_valid_vin(i) for i in range(count)]
        return [cls.create_invalid_vin() for _ in range(count)]


class UserFactory:
    """Factory for creating User entities and related data."""
    
    FIRST_NAMES = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    
    @classmethod
    def create_user(
        cls,
        telegram_id: Optional[int] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        preferences: Optional[UserPreferences] = None
    ) -> User:
        """Create a User entity with optional customization."""
        if telegram_id is None:
            telegram_id = random.randint(100000000, 999999999)
        
        if username is None:
            username = f"user_{telegram_id}"
        
        if first_name is None:
            first_name = random.choice(cls.FIRST_NAMES)
        
        if last_name is None:
            last_name = random.choice(cls.LAST_NAMES)
        
        if preferences is None:
            preferences = cls.create_preferences()
        
        return User.create(
            telegram_id=TelegramID(telegram_id),
            username=username,
            first_name=first_name,
            last_name=last_name,
            preferences=preferences
        )
    
    @classmethod
    def create_preferences(
        cls,
        preferred_decoder: Optional[str] = None,
        include_market_value: Optional[bool] = None,
        include_history: Optional[bool] = None,
        include_recalls: Optional[bool] = None,
        include_specs: Optional[bool] = None,
        format_preference: Optional[str] = None
    ) -> UserPreferences:
        """Create UserPreferences with optional customization."""
        return UserPreferences(
            preferred_decoder=preferred_decoder or random.choice(["nhtsa", "autodev"]),
            include_market_value=include_market_value if include_market_value is not None else random.choice([True, False]),
            include_history=include_history if include_history is not None else random.choice([True, False]),
            include_recalls=include_recalls if include_recalls is not None else random.choice([True, False]),
            include_specs=include_specs if include_specs is not None else random.choice([True, False]),
            format_preference=format_preference or random.choice(["standard", "detailed", "compact"])
        )


class VehicleFactory:
    """Factory for creating Vehicle entities and related data."""
    
    MANUFACTURERS = {
        "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Fit"],
        "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius"],
        "Ford": ["F-150", "Mustang", "Explorer", "Escape", "Focus"],
        "Chevrolet": ["Silverado", "Malibu", "Equinox", "Tahoe", "Corvette"],
        "BMW": ["3 Series", "5 Series", "X3", "X5", "M3"],
        "Mercedes-Benz": ["C-Class", "E-Class", "GLE", "S-Class", "A-Class"],
        "Tesla": ["Model 3", "Model S", "Model X", "Model Y", "Cybertruck"],
        "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Leaf"],
    }
    
    BODY_TYPES = ["Sedan", "SUV", "Truck", "Coupe", "Hatchback", "Convertible", "Wagon", "Van"]
    ENGINE_TYPES = ["2.0L 4-Cylinder", "3.5L V6", "5.0L V8", "1.5L Turbo", "Electric", "2.5L Hybrid"]
    TRANSMISSION_TYPES = ["Manual", "Automatic", "CVT", "Dual-Clutch", "Single-Speed"]
    FUEL_TYPES = ["Gasoline", "Diesel", "Electric", "Hybrid", "Plug-in Hybrid", "Hydrogen"]
    
    @classmethod
    def create_vehicle(
        cls,
        vin: Optional[str] = None,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        model_year: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None,
        service_used: str = "nhtsa"
    ) -> Vehicle:
        """Create a Vehicle entity with optional customization."""
        if vin is None:
            vin = VINFactory.create_valid_vin()
        
        if manufacturer is None:
            manufacturer = random.choice(list(cls.MANUFACTURERS.keys()))
        
        if model is None:
            model = random.choice(cls.MANUFACTURERS.get(manufacturer, ["Generic Model"]))
        
        if model_year is None:
            model_year = random.randint(2010, 2024)
        
        if attributes is None:
            attributes = cls.create_vehicle_attributes(manufacturer, model, model_year)
        
        return Vehicle.create_from_decode_result(
            vin=VINNumber(vin),
            manufacturer=manufacturer,
            model=model,
            model_year=ModelYear(model_year),
            attributes=attributes,
            service_used=service_used
        )
    
    @classmethod
    def create_vehicle_attributes(
        cls,
        manufacturer: str,
        model: str,
        year: int
    ) -> Dict[str, Any]:
        """Create realistic vehicle attributes."""
        return {
            "make": manufacturer,
            "model": model,
            "year": year,
            "body_type": random.choice(cls.BODY_TYPES),
            "engine": random.choice(cls.ENGINE_TYPES),
            "transmission": random.choice(cls.TRANSMISSION_TYPES),
            "fuel_type": random.choice(cls.FUEL_TYPES),
            "doors": random.choice([2, 4, 5]),
            "seats": random.choice([2, 5, 7, 8]),
            "drivetrain": random.choice(["FWD", "RWD", "AWD", "4WD"]),
            "mpg_city": random.randint(15, 35),
            "mpg_highway": random.randint(20, 45),
            "base_price": random.randint(20000, 80000),
            "safety_rating": round(random.uniform(3.0, 5.0), 1),
        }


class APIResponseFactory:
    """Factory for creating API response data."""
    
    @classmethod
    def create_nhtsa_response(
        cls,
        vin: str,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a mock NHTSA API response."""
        if not success:
            return {
                "Count": 0,
                "Message": error_message or "No data found",
                "Results": []
            }
        
        vehicle = VehicleFactory.create_vehicle(vin=vin)
        return {
            "Count": 1,
            "Message": "Results returned successfully",
            "Results": [{
                "Make": vehicle.manufacturer,
                "Model": vehicle.model,
                "ModelYear": str(vehicle.model_year.value),
                "VehicleType": "PASSENGER CAR",
                "BodyClass": "Sedan/Saloon",
                "EngineModel": "L15B7",
                "EngineCylinders": "4",
                "DisplacementL": "1.5",
                "FuelTypePrimary": "Gasoline",
                "TransmissionStyle": "CVT",
                "Doors": "4",
                "ErrorCode": "",
                "ErrorText": ""
            }]
        }
    
    @classmethod
    def create_autodev_response(
        cls,
        vin: str,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a mock AutoDev API response."""
        if not success:
            return {
                "success": False,
                "error": error_message or "VIN decode failed"
            }
        
        vehicle = VehicleFactory.create_vehicle(vin=vin)
        return {
            "success": True,
            "vin": vin,
            "make": {"name": vehicle.manufacturer},
            "model": {"name": vehicle.model},
            "years": [{"year": vehicle.model_year.value}],
            "engine": {
                "name": "1.5L I4",
                "cylinder": 4,
                "size": "1.5L",
                "fuelType": "Gasoline",
                "horsepower": 180,
                "torque": 177
            },
            "transmission": {
                "name": "CVT",
                "transmissionType": "Automatic",
                "numberOfSpeeds": "Variable"
            },
            "categories": {
                "primaryBodyType": "Sedan",
                "vehicleStyle": "4-Door Sedan",
                "epaClass": "Compact"
            },
            "specs": {
                "doors": 4,
                "seats": 5,
                "mpgCity": 32,
                "mpgHighway": 42
            }
        }


class TelegramDataFactory:
    """Factory for creating Telegram-related test data."""
    
    @classmethod
    def create_message_update(
        cls,
        text: str = "/start",
        user_id: int = 123456789,
        username: str = "testuser",
        chat_type: str = "private"
    ) -> Dict[str, Any]:
        """Create a Telegram message update."""
        return {
            "update_id": random.randint(100000000, 999999999),
            "message": {
                "message_id": random.randint(1, 999999),
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "last_name": "User",
                    "username": username,
                    "language_code": "en"
                },
                "chat": {
                    "id": user_id if chat_type == "private" else -random.randint(100000000, 999999999),
                    "type": chat_type,
                    "username": username if chat_type == "private" else None,
                    "title": None if chat_type == "private" else "Test Group"
                },
                "date": int(datetime.utcnow().timestamp()),
                "text": text
            }
        }
    
    @classmethod
    def create_callback_query_update(
        cls,
        data: str,
        user_id: int = 123456789,
        message_text: str = "Previous message"
    ) -> Dict[str, Any]:
        """Create a Telegram callback query update."""
        return {
            "update_id": random.randint(100000000, 999999999),
            "callback_query": {
                "id": str(random.randint(100000000, 999999999)),
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "testuser",
                    "language_code": "en"
                },
                "message": {
                    "message_id": random.randint(1, 999999),
                    "from": {
                        "id": 987654321,
                        "is_bot": True,
                        "first_name": "Test Bot",
                        "username": "testbot"
                    },
                    "chat": {
                        "id": user_id,
                        "type": "private",
                        "username": "testuser"
                    },
                    "date": int(datetime.utcnow().timestamp()),
                    "text": message_text
                },
                "data": data
            }
        }
    
    @classmethod
    def create_inline_query_update(
        cls,
        query: str,
        user_id: int = 123456789,
        offset: str = ""
    ) -> Dict[str, Any]:
        """Create a Telegram inline query update."""
        return {
            "update_id": random.randint(100000000, 999999999),
            "inline_query": {
                "id": str(random.randint(100000000, 999999999)),
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "testuser",
                    "language_code": "en"
                },
                "query": query,
                "offset": offset
            }
        }