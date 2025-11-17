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
    datasets_router
)

# Créer application FastAPI
app = FastAPI(
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

# Inclure routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(publications_router)
app.include_router(auteurs_router)
app.include_router(organisations_router)
app.include_router(themes_router)
app.include_router(datasets_router)

# Event handlers
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
