"""
Feedback API endpoints
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.feedback import Feedback
from app.services.auth_service import get_current_user_optional

router = APIRouter()


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: Optional[int] = None
    rating: int
    comment: Optional[str] = None


@router.post("/")
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="rating must be 1-5")
    feedback = Feedback(
        user_id=current_user.id if current_user else None,
        session_id=request.session_id,
        message_id=request.message_id,
        rating=request.rating,
        comment=request.comment
    )
    db.add(feedback)
    await db.commit()
    return {"status": "success"}
