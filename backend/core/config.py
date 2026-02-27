"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    anthropic_api_key: str
    anthropic_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./database/financial_advisor.db"
    
    # LLM Settings
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4-turbo-preview"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # RAG Settings
    vector_db_path: str = "./data/vector_store"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    
    # Memory Settings
    max_chat_history: int = 20
    session_timeout: int = 3600  # 1 hour in seconds
    
    # Safety & Ethics
    disclaimer_enabled: bool = True
    confidence_threshold: float = 0.6
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

