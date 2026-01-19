"""
Memory management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.memory_service import memory_service
from app.services.auth_service import get_current_user_optional

router = APIRouter()

class PreferenceRequest(BaseModel):
    session_id: str
    key: str
    value: Any

class ClearRequest(BaseModel):
    session_id: str
    clear_type: str  # 'chat', 'preferences', or 'all'

@router.post("/preferences")
async def save_preference(
    request: PreferenceRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Save user preference"""
    try:
        if current_user:
            user = current_user
        else:
            user = await memory_service.get_or_create_user(request.session_id, db)
        await memory_service.save_user_preference(
            user.id,
            request.key,
            request.value,
            db=db
        )
        return {"status": "success", "message": f"Preference '{request.key}' saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preferences/{session_id}")
async def get_preferences(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get all user preferences"""
    try:
        if current_user:
            user = current_user
        else:
            user = await memory_service.get_or_create_user(session_id, db)
        preferences = await memory_service.get_user_preferences(user.id, db=db)
        return {"preferences": preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
async def clear_memory(
    request: ClearRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Clear chat history and/or preferences"""
    try:
        if current_user:
            user = current_user
        else:
            user = await memory_service.get_or_create_user(request.session_id, db)
        
        if request.clear_type == "chat" or request.clear_type == "all":
            await memory_service.clear_chat_history(user.id, request.session_id, db=db)
        
        if request.clear_type == "preferences" or request.clear_type == "all":
            await memory_service.clear_user_preferences(user.id, db=db)
        
        return {
            "status": "success",
            "message": f"Cleared {request.clear_type}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

