"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    anthropic_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./database/financial_advisor.db"
    
    # LLM Settings
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "claude-sonnet-4-6"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # RAG Settings
    vector_db_path: str = "./data/vector_store"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    
    # Memory Settings
    max_chat_history: int = 40  # last N messages sent to LLM as context (e.g. 40 ≈ 20 exchanges)
    session_timeout: int = 3600  # 1 hour in seconds
    
    # Safety & Ethics
    disclaimer_enabled: bool = True
    confidence_threshold: float = 0.6
    require_citations: bool = True
    min_context_similarity: float = 0.2
    
    # Local Embeddings (default for this project)
    use_local_embeddings: bool = True

    # Code-switching constraints
    enable_language_style_constraint: bool = True
    eval_temperature_override: Optional[float] = 0.2
    language_style_retry_enabled: bool = True
    language_style_retry_max: int = 1

    # Authentication
    auth_secret_key: str = "change-me"
    auth_algorithm: str = "HS256"
    auth_access_token_minutes: int = 60 * 24 * 7
    password_reset_token_ttl_minutes: int = 30
    admin_bootstrap_key: str = ""

    # CORS
    cors_allow_origins: str = ""
    cors_allow_origin_regex: str = r"https://.*\.vercel\.app"

    # Live Market Data
    nse_market_data_url: [str] = "https://www.nse.co.ke/dataservices/market-statistics"
    nse_market_category: Optional[str] = None
    cbk_tbill_results_url: [str] = "https://www.centralbank.go.ke/bills-bonds/treasury-bills/"
    cbk_tbill_cache_ttl_seconds: int = 3600
    cma_mmf_weekly_url: Optional[str] = None
    cma_mmf_cache_ttl_seconds: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
