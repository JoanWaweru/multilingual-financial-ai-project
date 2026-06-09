"""
Database initialization and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import os

# Create database directory if it doesn't exist
db_path = settings.database_url.replace("sqlite:///", "").replace("sqlite+aiosqlite:///", "")
os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

# Fix database URL for async drivers
database_url = settings.database_url
if database_url.startswith("sqlite:///"):
    # Convert to async SQLite URL
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif database_url.startswith("postgresql://"):
    # Prefer asyncpg for Postgres
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine
engine = create_async_engine(
    database_url,
    echo=False,
    future=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    from app.models import user, chat_history, chat_session, user_preferences, feedback
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
