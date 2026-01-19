"""
Chat API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.rag_service import rag_service
from app.services.memory_service import memory_service
from app.core.config import settings
from app.services.auth_service import get_current_user_optional

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    session_id: str
    user_id: str
    retrieved_documents: int
    sources: List[Dict]
    disclaimer: Optional[str] = None

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Main chat endpoint with RAG"""
    try:
        # Get or create user
        if current_user:
            user = current_user
        else:
            user = await memory_service.get_or_create_user(request.session_id, db)
        
        # Get chat history
        chat_history = await memory_service.get_chat_history(
            user.id,
            request.session_id,
            db=db
        )
        
        # Get user preferences
        user_preferences = await memory_service.get_user_preferences(user.id, db=db)
        
        # Generate response using RAG
        rag_response = await rag_service.retrieve_and_generate(
            query=request.message,
            chat_history=chat_history,
            user_preferences=user_preferences
        )
        
        # Save user message
        await memory_service.save_chat_message(
            user.id,
            request.session_id,
            "user",
            request.message,
            db=db
        )
        
        # Save assistant response
        await memory_service.save_chat_message(
            user.id,
            request.session_id,
            "assistant",
            rag_response['response'],
            metadata={
                'confidence': rag_response['confidence'],
                'sources': rag_response.get('sources', [])
            },
            db=db
        )
        
        # Add disclaimer if enabled
        disclaimer = None
        if settings.disclaimer_enabled:
            disclaimer = "⚠️ Disclaimer: This AI is not a licensed financial advisor. Please consult with qualified professionals for major financial decisions."
        
        return ChatResponse(
            response=rag_response['response'],
            confidence=rag_response['confidence'],
            session_id=request.session_id,
            user_id=user.id,
            retrieved_documents=rag_response.get('retrieved_documents', 0),
            sources=rag_response.get('sources', []),
            disclaimer=disclaimer
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a session"""
    try:
        user = await memory_service.get_or_create_user(session_id, db)
        history = await memory_service.get_chat_history(
            user.id,
            session_id,
            limit=limit,
            db=db
        )
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

