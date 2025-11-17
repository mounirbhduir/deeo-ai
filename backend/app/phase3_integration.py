"""
Intégration Phase 3 dans l'application FastAPI.

Ce module fournit:
- Initialisation logging structuré
- Initialisation scheduler APScheduler
- Middleware logging requêtes
- Lifecycle events (startup/shutdown)
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import uuid

from app.logging import configure_structlog, get_logger, bind_context, clear_context
from app.scheduler import get_scheduler
from app.config import settings

# Logger
logger = get_logger(__name__)


# ===== Lifespan Events =====

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan events pour FastAPI.
    
    Gère:
    - Startup: Initialize logging & scheduler
    - Shutdown: Cleanup graceful
    
    Args:
        app: Application FastAPI
        
    Yields:
        None
    """
    # ===== STARTUP =====
    logger.info("application.starting")
    
    # 1. Configure logging
    configure_structlog(
        log_level=settings.LOG_LEVEL,
        json_logs=settings.ENVIRONMENT == "production",
        log_file=settings.LOG_FILE if hasattr(settings, 'LOG_FILE') else None
    )
    logger.info("logging.configured", 
               log_level=settings.LOG_LEVEL,
               json_logs=settings.ENVIRONMENT == "production")
    
    # 2. Initialize scheduler
    scheduler = get_scheduler()
    scheduler.initialize()
    scheduler.start()
    logger.info("scheduler.started")
    
    # 3. Application ready
    logger.info("application.ready", 
               environment=settings.ENVIRONMENT,
               debug=settings.DEBUG)
    
    yield  # Application runs here
    
    # ===== SHUTDOWN =====
    logger.info("application.shutting_down")
    
    # 1. Stop scheduler
    scheduler.shutdown(wait=True)
    logger.info("scheduler.stopped")
    
    # 2. Application stopped
    logger.info("application.stopped")


# ===== Middleware Logging Requêtes =====

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour logger toutes les requêtes HTTP.
    
    Logs:
    - Entrée requête (method, path, request_id)
    - Sortie requête (status, duration_ms)
    - Erreurs
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request et log.
        
        Args:
            request: Requête HTTP
            call_next: Handler suivant
            
        Returns:
            Response HTTP
        """
        # Générer request_id unique
        request_id = str(uuid.uuid4())
        
        # Bind request_id au contexte (thread-safe)
        bind_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )
        
        # Log entrée requête
        logger.info("request.started",
                   method=request.method,
                   path=request.url.path,
                   query_params=dict(request.query_params),
                   user_agent=request.headers.get("user-agent"))
        
        # Mesurer durée
        start_time = time.time()
        
        try:
            # Traiter requête
            response = await call_next(request)
            
            # Calculer durée
            duration_ms = (time.time() - start_time) * 1000
            
            # Log sortie requête
            logger.info("request.completed",
                       status_code=response.status_code,
                       duration_ms=round(duration_ms, 2))
            
            # Ajouter request_id dans headers response
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log erreur
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error("request.error",
                        error_type=type(e).__name__,
                        error_message=str(e),
                        duration_ms=round(duration_ms, 2),
                        exc_info=True)
            
            raise
            
        finally:
            # Nettoyer contexte pour éviter fuites
            clear_context()


# ===== Exception Handler =====

async def log_unhandled_exception(request: Request, exc: Exception) -> None:
    """
    Log exceptions non gérées.
    
    Args:
        request: Requête HTTP
        exc: Exception levée
    """
    logger.error("exception.unhandled",
                method=request.method,
                path=request.url.path,
                error_type=type(exc).__name__,
                error_message=str(exc),
                exc_info=True)


# ===== Helper Integration =====

def integrate_phase3(app: FastAPI) -> None:
    """
    Intègre Phase 3 dans l'application FastAPI.
    
    Ajoute:
    - Lifespan events
    - Middleware logging
    - Exception handlers
    
    Args:
        app: Application FastAPI
        
    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> integrate_phase3(app)
    """
    # Note: Lifespan doit être défini à la création de FastAPI
    # app.router.lifespan_context = lifespan  # Ne fonctionne pas dynamiquement
    
    # Ajouter middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("phase3.integrated",
               middleware=["RequestLoggingMiddleware"])


# ===== Updated main.py Instructions =====

"""
Pour intégrer Phase 3 dans main.py:

```python
from fastapi import FastAPI
from app.phase3_integration import lifespan, integrate_phase3

# Créer app avec lifespan
app = FastAPI(
    title="DEEO.AI API",
    version="1.0.0",
    lifespan=lifespan  # <-- Ajouter ici
)

# Intégrer middleware
integrate_phase3(app)

# ... reste du code ...
```
"""
