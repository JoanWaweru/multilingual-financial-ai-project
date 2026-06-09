"""
Chat history model for storing conversation context
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    session_id = Column(String, index=True)
    role = Column(String)  # 'user' or 'assistant'
    message = Column(Text)
    message_metadata = Column(Text)  # JSON string for additional data (renamed from 'metadata' to avoid SQLAlchemy conflict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, role={self.role})>"

