"""
DEEO.AI - Point d'entrée principal de l'API FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1 import health

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

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Actions au démarrage de l'application"""
    print(f"🚀 DEEO.AI API démarrée - Environnement: {settings.ENVIRONMENT}")

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
