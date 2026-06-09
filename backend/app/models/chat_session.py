"""
Chat session model for grouping conversations per user
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    session_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    last_message = Column(Text, nullable=True)
    last_role = Column(String, nullable=True)
    pinned = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
