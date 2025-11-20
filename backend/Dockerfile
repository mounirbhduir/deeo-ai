# ==================================================================
# DOCKERFILE - BACKEND FASTAPI
# ==================================================================
#
# Description : Image Docker pour API FastAPI
# Usage       : docker build -t deeo-api -f backend/Dockerfile backend/
#
# ==================================================================

FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Mounir <mounir@deeo.ai>"
LABEL description="DEEO.AI Backend API - FastAPI"
LABEL version="0.4.0"

# Variables environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Créer répertoire application
WORKDIR /app

# Copier requirements
COPY requirements.txt .

# Installer dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier code application
COPY . .

# Créer répertoire logs
RUN mkdir -p /app/logs

# Exposer port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Commande par défaut (mode dev avec hot reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
