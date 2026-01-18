"""
User preferences model for long-term memory
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    preference_key = Column(String, index=True)  # e.g., 'risk_level', 'language', 'goals'
    preference_value = Column(Text)  # JSON string for complex values
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserPreferences(key={self.preference_key}, value={self.preference_value})>"

