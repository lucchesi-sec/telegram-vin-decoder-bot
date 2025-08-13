"""JWT token handling for unified authentication."""

from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import os

# TODO: Move to configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


class JWTHandler:
    """Handles JWT token creation and validation."""
    
    @staticmethod
    def create_access_token(user_id: int, telegram_id: int) -> str:
        """Create a JWT access token for a user."""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "user_id": user_id,
            "telegram_id": telegram_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract user ID from JWT token."""
    payload = JWTHandler.decode_token(credentials.credentials)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id


def get_current_telegram_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract Telegram ID from JWT token."""
    payload = JWTHandler.decode_token(credentials.credentials)
    telegram_id = payload.get("telegram_id")
    if telegram_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return telegram_id


# Optional dependency for endpoints that can work with or without auth
def get_optional_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[int]:
    """Extract user ID from JWT token if present, otherwise return None."""
    if credentials is None:
        return None
    try:
        payload = JWTHandler.decode_token(credentials.credentials)
        return payload.get("user_id")
    except HTTPException:
        return None