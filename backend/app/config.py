"""
Configuration de l'application DEEO.AI

Utilise Pydantic Settings pour gérer les variables d'environnement.
"""
from typing import Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Configuration de l'application DEEO.AI.
    
    Les variables peuvent être définies dans :
    - Fichier .env
    - Variables d'environnement système
    - Valeurs par défaut ci-dessous
    """
    
    # Application
    APP_NAME: str = "DEEO.AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # ===== PHASE 3 - LOGGING =====
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None  # Path to log file (None = stdout only)
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://deeo_user:deeo_password@localhost:5432/deeo_ai"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL_DEFAULT: int = 3600  # 1 hour
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS - Include port 5174 for staging frontend
    CORS_ORIGINS: Union[str, list[str]] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:8000"]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Parse CORS_ORIGINS from string or list.

        Accepts:
        - JSON array: '["http://localhost:5173", "http://localhost:8000"]'
        - CSV string: "http://localhost:5173,http://localhost:8000"
        - Python list: ["http://localhost:5173", "http://localhost:8000"]

        Returns:
        - list[str]: Parsed list of origins
        """
        if isinstance(v, str):
            # Try JSON parsing first
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass

            # Fallback to CSV parsing
            return [origin.strip() for origin in v.split(",") if origin.strip()]

        # Already a list
        return v

    # Pagination
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 1000
    
    # Security (pour Phase 3+)
    SECRET_KEY: str = "changeme-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs (Phase 3)
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    ARXIV_MAX_RESULTS: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Instance globale
settings = Settings()
