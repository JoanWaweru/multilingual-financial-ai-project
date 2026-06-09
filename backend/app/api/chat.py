"""
Chat API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.rag_service import rag_service
from app.services.memory_service import memory_service
from app.core.config import settings
from app.services.auth_service import get_current_user_optional, get_current_user

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
    evidence: List[Dict] = []
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
                'sources': rag_response.get('sources', []),
                'evidence': rag_response.get('evidence', [])
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
            evidence=rag_response.get('evidence', []),
            disclaimer=disclaimer
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get chat history for a session"""
    try:
        if current_user:
            user = current_user
        else:
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


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    sessions = await memory_service.get_user_sessions(current_user.id, db)
    return {"sessions": sessions}


class RenameRequest(BaseModel):
    title: str


@router.post("/sessions/{session_id}/rename")
async def rename_session(
    session_id: str,
    request: RenameRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await memory_service.rename_session(current_user.id, session_id, request.title, db)
    return {"status": "success"}


class PinRequest(BaseModel):
    pinned: bool


@router.post("/sessions/{session_id}/pin")
async def pin_session(
    session_id: str,
    request: PinRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await memory_service.pin_session(current_user.id, session_id, request.pinned, db)
    return {"status": "success"}


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    await memory_service.soft_delete_session(current_user.id, session_id, db)
    return {"status": "success"}


@router.get("/export/{session_id}")
async def export_session(
    session_id: str,
    format: str = "csv",
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    history = await memory_service.get_chat_history(
        current_user.id,
        session_id,
        limit=1000,
        db=db
    )
    if format not in ("csv", "pdf"):
        raise HTTPException(status_code=400, detail="format must be csv or pdf")

    if format == "csv":
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["role", "message"])
        for item in history:
            writer.writerow([item.get("role"), item.get("message")])
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=chat_{session_id}.csv"}
        )

    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Chat Session: {session_id}", ln=True)
    for item in history:
        line = f"{item.get('role')}: {item.get('message')}"
        line = line.replace("\t", " ").replace("\r", " ")
        line = " ".join(line.split())
        if not line:
            continue
        try:
            pdf.multi_cell(0, 8, line)
        except Exception:
            safe_line = (line[:3000] + "...") if len(line) > 3000 else line
            pdf.multi_cell(0, 8, safe_line)
    pdf_bytes = pdf.output(dest="S")
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode("latin-1")
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=chat_{session_id}.pdf"}
    )

