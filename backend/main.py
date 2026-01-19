"""
Main FastAPI application for Conversational AI Financial Advisor
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from app.api import chat, memory, documents, auth, admin, feedback, eval
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(
    title="Kenyan Financial Advisor AI",
    description="Conversational AI system for personal finance advice in Kenya",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(eval.router, prefix="/api/eval", tags=["eval"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and vector store on startup"""
    await init_db()
    print("✅ Database initialized")
    print("✅ Application ready")

@app.get("/")
async def root():
    return {
        "message": "Kenyan Financial Advisor AI API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

