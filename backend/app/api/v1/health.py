"""
Router pour health checks et status API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis

from app.database import get_db
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Endpoint de health check
    
    Vérifie:
    - API est opérationnelle
    - Connexion PostgreSQL
    - Connexion Redis
    """
    status = {
        "status": "healthy",
        "api": "ok",
        "database": "unknown",
        "cache": "unknown"
    }
    
    # Test connexion PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    # Test connexion Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        status["cache"] = "ok"
    except Exception as e:
        status["cache"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    return status


@router.get("/version")
async def version():
    """Retourne la version de l'API"""
    return {
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }
