"""
Configuration base de données PostgreSQL avec SQLAlchemy async
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

# Créer engine async
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base pour modèles SQLAlchemy
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency pour obtenir une session de base de données
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
