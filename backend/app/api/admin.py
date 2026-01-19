"""
Admin API endpoints for analytics and feedback
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.user import User
from app.models.chat_history import ChatHistory
from app.models.feedback import Feedback
from app.services.auth_service import require_roles

router = APIRouter()


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    users_count = await db.execute(select(func.count()).select_from(User))
    chats_count = await db.execute(select(func.count()).select_from(ChatHistory))
    feedback_count = await db.execute(select(func.count()).select_from(Feedback))
    return {
        "users": users_count.scalar_one(),
        "messages": chats_count.scalar_one(),
        "feedback": feedback_count.scalar_one()
    }


@router.get("/feedback")
async def list_feedback(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    result = await db.execute(
        select(Feedback).order_by(Feedback.created_at.desc()).limit(200)
    )
    items = result.scalars().all()
    return {
        "feedback": [
            {
                "id": f.id,
                "user_id": f.user_id,
                "session_id": f.session_id,
                "message_id": f.message_id,
                "rating": f.rating,
                "comment": f.comment,
                "created_at": f.created_at.isoformat() if f.created_at else None
            }
            for f in items
        ]
    }
