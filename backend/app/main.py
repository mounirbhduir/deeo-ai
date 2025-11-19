"""
DEEO.AI - Point d'entrée principal de l'API FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1 import health
from app.api.v1 import (
    publications_router,
    auteurs_router,
    organisations_router,
    themes_router,
    datasets_router,
    statistics_router
)
from app.api.v1.publications_search_mock import router as publications_search_router
from app.api.v1.authors_mock import router as authors_mock_router
from app.api.v1.organisations_mock import router as organisations_mock_router
from app.api.v1.graphs_mock import router as graphs_mock_router
from app.phase3_integration import lifespan, integrate_phase3

# Créer application FastAPI
app = FastAPI(
    lifespan=lifespan,
    title="DEEO.AI API",
    description="AI Dynamic Emergence and Evolution Observatory",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Integrate Phase 3
integrate_phase3(app)

# Inclure routers
# IMPORTANT: Search router MUST come BEFORE publications_router
# to avoid /search being matched by /{publication_id}
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(statistics_router)
app.include_router(publications_search_router, prefix="/api/v1/publications", tags=["publications-search"])
app.include_router(authors_mock_router, prefix="/api/v1/authors", tags=["authors-mock"])
app.include_router(organisations_mock_router, prefix="/api/v1/organisations", tags=["organisations-mock"])
app.include_router(graphs_mock_router, prefix="/api/v1/graphs", tags=["graphs-mock"])
app.include_router(publications_router)
app.include_router(auteurs_router)
app.include_router(organisations_router)
app.include_router(themes_router)
app.include_router(datasets_router)

# Event handlers (deprecated, but kept for backward compatibility)
@app.on_event("startup")
async def startup_event():
    """Actions au démarrage de l'application"""
    print(f"🚀 DEEO.AI API démarrée - Version: {settings.APP_VERSION} - Debug: {settings.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    """Actions à l'arrêt de l'application"""
    print("🛑 DEEO.AI API arrêtée")

# Root endpoint
@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Welcome to DEEO.AI API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }
