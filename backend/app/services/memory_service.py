"""
Memory service for managing chat history and user preferences
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Dict, Optional
from app.models.user import User
from app.models.chat_history import ChatHistory
from app.models.user_preferences import UserPreferences
from app.core.config import settings
import json
from datetime import datetime, timedelta

class MemoryService:
    """Service for managing short-term and long-term memory"""
    
    async def get_or_create_user(self, session_id: str, db: AsyncSession) -> User:
        """Get existing user or create new one"""
        result = await db.execute(
            select(User).where(User.session_id == session_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(session_id=session_id)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    async def save_chat_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        message: str,
        metadata: Dict = None,
        db: AsyncSession = None
    ):
        """Save a chat message to history"""
        chat_entry = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            message=message,
            message_metadata=json.dumps(metadata) if metadata else None
        )
        db.add(chat_entry)
        await db.commit()
    
    async def get_chat_history(
        self,
        user_id: str,
        session_id: str,
        limit: int = None,
        db: AsyncSession = None
    ) -> List[Dict]:
        """Retrieve chat history"""
        limit = limit or settings.max_chat_history
        
        result = await db.execute(
            select(ChatHistory)
            .where(
                (ChatHistory.user_id == user_id) | (ChatHistory.session_id == session_id)
            )
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
        )
        
        history = result.scalars().all()
        
        # Format for LLM
        formatted = []
        for entry in reversed(history):  # Reverse to get chronological order
            formatted.append({
                'role': entry.role,
                'message': entry.message,
                'metadata': json.loads(entry.message_metadata) if entry.message_metadata else {}
            })
        
        return formatted
    
    async def clear_chat_history(
        self,
        user_id: str,
        session_id: str,
        db: AsyncSession = None
    ):
        """Clear chat history for a user"""
        await db.execute(
            delete(ChatHistory).where(
                (ChatHistory.user_id == user_id) | (ChatHistory.session_id == session_id)
            )
        )
        await db.commit()
    
    async def save_user_preference(
        self,
        user_id: str,
        key: str,
        value: any,
        db: AsyncSession = None
    ):
        """Save or update a user preference"""
        # Check if preference exists
        result = await db.execute(
            select(UserPreferences).where(
                UserPreferences.user_id == user_id,
                UserPreferences.preference_key == key
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.preference_value = json.dumps(value) if not isinstance(value, str) else value
            existing.updated_at = datetime.utcnow()
        else:
            new_pref = UserPreferences(
                user_id=user_id,
                preference_key=key,
                preference_value=json.dumps(value) if not isinstance(value, str) else value
            )
            db.add(new_pref)
        
        await db.commit()
    
    async def get_user_preferences(
        self,
        user_id: str,
        db: AsyncSession = None
    ) -> Dict:
        """Get all user preferences"""
        result = await db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        preferences = result.scalars().all()
        
        prefs_dict = {}
        for pref in preferences:
            try:
                value = json.loads(pref.preference_value)
            except:
                value = pref.preference_value
            prefs_dict[pref.preference_key] = value
        
        return prefs_dict
    
    async def clear_user_preferences(
        self,
        user_id: str,
        db: AsyncSession = None
    ):
        """Clear all user preferences"""
        await db.execute(
            delete(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        await db.commit()

memory_service = MemoryService()

