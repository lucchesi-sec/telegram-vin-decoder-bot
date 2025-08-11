"""SQLAlchemy User VIN History model."""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class UserVINHistoryModel(Base):
    """User VIN history database model."""
    
    __tablename__ = "user_vin_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    vin = Column(String(17), nullable=False)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=True)
    
    decoded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("UserModel", backref="vin_history")
    vehicle = relationship("VehicleModel", backref="user_lookups")
    
    __table_args__ = (
        Index('idx_user_history', 'user_id', 'decoded_at'),
        Index('idx_user_vin', 'user_id', 'vin'),
    )
    
    def __repr__(self):
        return f"<UserVINHistoryModel(id={self.id}, user_id={self.user_id}, vin={self.vin})>"