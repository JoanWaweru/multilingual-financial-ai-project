"""
Memory service for managing chat history and user preferences
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Optional
from app.models.user import User
from app.models.chat_history import ChatHistory
from app.models.chat_session import ChatSession
from app.services.llm_service import llm_service
from datetime import datetime
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
        await self.get_or_create_session(user_id, session_id, db)
        await self._update_session_from_message(user_id, session_id, role, message, db)

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
                (ChatHistory.user_id == user_id) & (ChatHistory.session_id == session_id)
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

    async def get_user_sessions(self, user_id: str, db: AsyncSession) -> List[Dict]:
        """Return session summaries for a user."""
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id, ChatSession.deleted_at.is_(None))
            .order_by(ChatSession.pinned.desc(), ChatSession.last_updated.desc())
        )
        sessions = result.scalars().all()
        if not sessions:
            await self._backfill_sessions_from_history(user_id, db)
            result = await db.execute(
                select(ChatSession)
                .where(ChatSession.user_id == user_id, ChatSession.deleted_at.is_(None))
                .order_by(ChatSession.pinned.desc(), ChatSession.last_updated.desc())
            )
            sessions = result.scalars().all()
        return [
            {
                "session_id": s.session_id,
                "title": s.title or "",
                "summary": s.summary or "",
                "last_message": s.last_message or "",
                "last_role": s.last_role or "",
                "pinned": bool(s.pinned),
                "last_updated": s.last_updated.isoformat() if s.last_updated else None
            }
            for s in sessions
        ]

    async def get_or_create_session(self, user_id: str, session_id: str, db: AsyncSession) -> ChatSession:
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            return session
        session = ChatSession(user_id=user_id, session_id=session_id, title=None)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def rename_session(self, user_id: str, session_id: str, title: str, db: AsyncSession) -> None:
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id, ChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return
        session.title = title.strip()[:80] if title else session.title
        await db.commit()

    async def pin_session(self, user_id: str, session_id: str, pinned: bool, db: AsyncSession) -> None:
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id, ChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return
        session.pinned = bool(pinned)
        await db.commit()

    async def soft_delete_session(self, user_id: str, session_id: str, db: AsyncSession) -> None:
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id, ChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return
        session.deleted_at = datetime.utcnow()
        await db.commit()

    async def _update_session_from_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        message: str,
        db: AsyncSession
    ) -> None:
        result = await db.execute(
            select(ChatSession).where(ChatSession.session_id == session_id, ChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return
        if not session.title and role == "user":
            session.title = await llm_service.summarize_session_title(message)
        if not session.summary and role == "user":
            session.summary = session.title or self._summarize_title(message)
        session.last_message = message
        session.last_role = role
        await db.commit()

    def _summarize_title(self, message: str) -> str:
        trimmed = " ".join(message.strip().split())
        return trimmed[:60] + ("..." if len(trimmed) > 60 else "")

    async def _backfill_sessions_from_history(self, user_id: str, db: AsyncSession) -> None:
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
        )
        entries = result.scalars().all()
        seen = set()
        for entry in entries:
            if entry.session_id in seen:
                continue
            seen.add(entry.session_id)
            session = ChatSession(
                user_id=user_id,
                session_id=entry.session_id,
                title=self._summarize_title(entry.message),
                summary=self._summarize_title(entry.message),
                last_message=entry.message,
                last_role=entry.role
            )
            db.add(session)
        if seen:
            await db.commit()
    
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

    async def claim_guest_session(
        self,
        authenticated_user_id: str,
        browser_session_id: str,
        db: AsyncSession
    ) -> Dict:
        """
        Attach anonymous browser-session chats to the logged-in account.
        Guest users are created with User.session_id == browser session UUID.
        """
        result = await db.execute(
            select(User).where(User.session_id == browser_session_id)
        )
        guest_user = result.scalar_one_or_none()

        if not guest_user or guest_user.id == authenticated_user_id:
            return {"merged": False, "reason": "nothing_to_merge"}

        if guest_user.email:
            return {"merged": False, "reason": "session_owned_by_other_account"}

        await db.execute(
            update(ChatHistory)
            .where(ChatHistory.user_id == guest_user.id)
            .values(user_id=authenticated_user_id)
        )
        await db.execute(
            update(ChatSession)
            .where(ChatSession.user_id == guest_user.id)
            .values(user_id=authenticated_user_id)
        )
        await db.execute(
            update(UserPreferences)
            .where(UserPreferences.user_id == guest_user.id)
            .values(user_id=authenticated_user_id)
        )

        try:
            await db.execute(delete(User).where(User.id == guest_user.id))
            await db.commit()
        except IntegrityError:
            await db.rollback()
            await db.commit()

        return {"merged": True, "browser_session_id": browser_session_id}

memory_service = MemoryService()

