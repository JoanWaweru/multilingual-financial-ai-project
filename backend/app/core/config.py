"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./database/financial_advisor.db"
    
    # LLM Settings
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"  # Changed from gpt-4-turbo-preview to gpt-4o-mini (more widely available)
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
    require_citations: bool = False
    min_context_similarity: float = 0.0
    
    # Local Embeddings (fallback when OpenAI quota is exceeded)
    use_local_embeddings: bool = False

    # Code-switching constraints
    enable_language_style_constraint: bool = True
    eval_temperature_override: Optional[float] = 0.2
    language_style_retry_enabled: bool = True
    language_style_retry_max: int = 1

    # Authentication
    auth_secret_key: str = "change-me"
    auth_algorithm: str = "HS256"
    auth_access_token_minutes: int = 60 * 24 * 7

    # Live Market Data (optional)
    nse_market_data_url: Optional[str] = None
    nse_market_category: Optional[str] = None
    nse_market_cache_ttl_seconds: int = 900
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
