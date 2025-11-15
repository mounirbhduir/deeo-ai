# DEEO.AI - Architecture

## Vue d'Ensemble

DEEO.AI est un observatoire open source pour le suivi et l'analyse de l'évolution de l'intelligence artificielle.

## Architecture Système

### Phase 1 - PoC Local (Actuel)
```
┌─────────────────────────────────────────────────────────┐
│                    DEEO.AI System                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────┐  │
│  │   FastAPI    │   │  PostgreSQL  │   │   Redis   │  │
│  │     API      │──▶│   Database   │   │   Cache   │  │
│  │  (Port 8000) │   │  (Port 5432) │   │(Port 6379)│  │
│  └──────────────┘   └──────────────┘   └───────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Composants

#### 1. API FastAPI
- **Port**: 8000
- **Technologie**: FastAPI 0.104, Python 3.11
- **Responsabilités**:
  - Endpoints REST
  - Validation données (Pydantic)
  - Documentation auto (OpenAPI)
  - CORS configuration

#### 2. PostgreSQL
- **Port**: 5432
- **Version**: 15.5
- **Extensions**: uuid-ossp, pg_trgm, pg_stat_statements
- **Bases**: deeo_ai (production), deeo_ai_test (tests)
- **Responsabilités**:
  - Stockage données
  - Relations entités
  - Recherche full-text

#### 3. Redis
- **Port**: 6379
- **Version**: 7
- **Responsabilités**:
  - Cache requêtes
  - Sessions
  - Rate limiting (futur)

## Architecture Logicielle

### Layered Architecture
```
┌─────────────────────────────────────────┐
│         Controllers (Routers)           │  ← Endpoints FastAPI
├─────────────────────────────────────────┤
│         Services (Business Logic)       │  ← Logique métier
├─────────────────────────────────────────┤
│      Repositories (Data Access)         │  ← Accès données
├─────────────────────────────────────────┤
│         Models (SQLAlchemy)             │  ← Entités DB
└─────────────────────────────────────────┘
```

## Tests

- **Framework**: pytest + pytest-asyncio
- **Coverage**: 79% (Phase 1)
- **Base test**: deeo_ai_test (PostgreSQL)

## Déploiement

### Docker Compose

3 conteneurs orchestrés:
- `deeo-postgres` - Base de données
- `deeo-redis` - Cache
- `deeo-api` - API FastAPI

### Variables d'Environnement

Voir `.env.example` pour configuration.

## Évolution

### Phase 2 (Prochaine)
- Modèles SQLAlchemy complets (31 tables)
- API CRUD complète
- Pipeline collecte arXiv

### Phase 3
- Enrichissement Semantic Scholar
- Cache Redis avancé
- Tests >75% coverage

### Phase 4
- Frontend React
- Visualisations
- Documentation complète

---

**Version**: 1.0.0  
**Date**: November 15, 2025