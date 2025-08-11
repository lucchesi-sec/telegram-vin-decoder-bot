"""SQLAlchemy Vehicle model."""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Index
from sqlalchemy.sql import func
from .base import Base


class VehicleModel(Base):
    """Vehicle database model for caching VIN decode results."""
    
    __tablename__ = "vehicles"
    
    id = Column(String, primary_key=True)
    vin = Column(String(17), unique=True, nullable=False, index=True)
    
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    manufacturer = Column(String(200), nullable=True)
    
    service_used = Column(String(50), nullable=True)
    
    raw_data = Column(JSON, nullable=False)
    
    basic_info = Column(JSON, nullable=True)
    specifications = Column(JSON, nullable=True)
    safety_ratings = Column(JSON, nullable=True)
    
    error_message = Column(Text, nullable=True)
    
    decoded_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_vin_expires', 'vin', 'expires_at'),
        Index('idx_make_model_year', 'make', 'model', 'year'),
    )
    
    def __repr__(self):
        return f"<VehicleModel(id={self.id}, vin={self.vin}, make={self.make}, model={self.model}, year={self.year})>"