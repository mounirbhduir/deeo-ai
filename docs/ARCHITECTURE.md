# 🏗️ DEEO.AI - ARCHITECTURE TECHNIQUE

**Projet** : DEEO.AI - AI Dynamic Emergence and Evolution Observatory
**Phase** : Phase 2 - Backend Complete
**Date** : 17 Novembre 2025
**Version** : 2.0.0

---

## 📋 SOMMAIRE

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture Système](#architecture-système)
3. [Architecture Logicielle](#architecture-logicielle)
4. [Modèle de Données](#modèle-de-données)
5. [API REST](#api-rest)
6. [Pipeline de Développement](#pipeline-de-développement)
7. [Patterns & Principes](#patterns--principes)
8. [Décisions Architecturales](#décisions-architecturales)
9. [Évolution Architecture](#évolution-architecture)

---

## Vue d'Ensemble

DEEO.AI est un **observatoire open source** pour le suivi et l'analyse de l'évolution de l'intelligence artificielle. Le projet collecte, enrichit et analyse automatiquement les publications scientifiques, auteurs, organisations et thématiques du domaine de l'IA.

### Objectifs Architecturaux

- **Scalabilité** : Supporter 15,000-25,000 publications
- **Performance** : Temps réponse API <200ms
- **Maintenabilité** : Architecture layered, tests complets
- **Extensibilité** : Ajout facile de nouvelles sources, modèles ML
- **Qualité** : Coverage ≥75%, tests automatisés

### Principes Fondamentaux

1. **Separation of Concerns** - Chaque layer a une responsabilité unique
2. **Dependency Inversion** - Dépendances vers abstractions
3. **DRY (Don't Repeat Yourself)** - Réutilisation code
4. **SOLID Principles** - Code propre et maintenable
5. **Test-Driven Development** - Tests dès la conception

---

## Architecture Système

### Phase 2 - Backend Complete (Actuel)

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEEO.AI System                           │
│                    (Phase 2 - Backend Complete)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐   ┌──────────────────┐   ┌───────────┐  │
│  │    FastAPI       │   │   PostgreSQL     │   │   Redis   │  │
│  │   Backend API    │──▶│   Database       │   │   Cache   │  │
│  │  (Port 8000)     │   │  (Port 5432)     │   │(Port 6379)│  │
│  │                  │   │                  │   │           │  │
│  │ 6 Routers        │   │ 29 Tables        │   │ Ready     │  │
│  │ 27 Endpoints     │   │ 31 Models        │   │           │  │
│  │ Swagger UI       │   │ Alembic          │   │           │  │
│  └──────────────────┘   └──────────────────┘   └───────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Tests Suite                          │  │
│  │  178 tests passing (100%) | Coverage 68-94%            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Composants Infrastructure

#### 1. API FastAPI

- **Port** : 8000
- **Technologie** : FastAPI 0.104+, Python 3.11+, async/await
- **Responsabilités** :
  - Endpoints REST CRUD
  - Validation données (Pydantic)
  - Documentation auto (Swagger UI / ReDoc)
  - CORS configuration
  - Gestion erreurs HTTP
- **Performance** : Async I/O, ~200ms response time
- **URLs** :
  - API Base : http://localhost:8000/api
  - Swagger UI : http://localhost:8000/api/docs
  - ReDoc : http://localhost:8000/api/redoc

#### 2. PostgreSQL

- **Port** : 5432
- **Version** : 15.5
- **Extensions** : uuid-ossp, pg_trgm, pg_stat_statements
- **Bases** :
  - `deeo_ai` (production)
  - `deeo_ai_test` (tests)
- **Tables** : 29 tables (31 modèles SQLAlchemy)
- **Responsabilités** :
  - Stockage données persistant
  - Relations entités (Many-to-Many)
  - Recherche full-text (pg_trgm)
  - Indexes performance
- **Volume attendu Phase 3** : 15,000-25,000 publications

#### 3. Redis

- **Port** : 6379
- **Version** : 7.0
- **Configuration** : No password (dev), maxmemory-policy allkeys-lru
- **Responsabilités** :
  - Cache requêtes API (Phase 3)
  - Sessions utilisateur (Phase 4)
  - Rate limiting (Phase 4)
  - Job queue (Phase 3)
- **TTL Strategy (Phase 3)** :
  - Publications : 1h
  - Auteurs : 24h
  - Classifications : 7 jours
  - Embeddings : 30 jours

---

## Architecture Logicielle

### Layered Architecture (5 Layers)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT                                  │
│              (Browser, cURL, Postman, etc.)                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/JSON
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API LAYER (Routers)                          │
│  - FastAPI routers (6 routers, 27 endpoints)                   │
│  - Request validation (Pydantic)                                │
│  - Response formatting                                          │
│  - Error handling (HTTPException)                               │
│  - Pagination, filtering                                        │
│                                                                 │
│  Files: backend/app/api/v1/*.py                                │
│  Tests: backend/tests/api/*.py (70 tests, 68% coverage)        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SCHEMA LAYER (Validation)                      │
│  - Pydantic schemas (24 schemas)                                │
│  - Input validation (Create, Update)                            │
│  - Output serialization (Response)                              │
│  - Custom validators (DOI, ORCID, URL)                          │
│                                                                 │
│  Files: backend/app/schemas/*.py                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                SERVICE LAYER (Business Logic)                   │
│  - Service classes (5 services)                                 │
│  - Business rules validation                                    │
│  - Multi-repository orchestration                               │
│  - Transaction management                                       │
│  - Complex operations                                           │
│                                                                 │
│  Files: backend/app/services/*.py                               │
│  Tests: backend/tests/services/*.py (46 tests, 86% coverage)   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              REPOSITORY LAYER (Data Access)                     │
│  - Repository classes (6 repositories)                          │
│  - CRUD operations                                              │
│  - Specialized queries                                          │
│  - Database abstraction                                         │
│  - SQLAlchemy session management                                │
│                                                                 │
│  Files: backend/app/repositories/*.py                           │
│  Tests: backend/tests/repositories/*.py (62 tests, 94% cov)    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MODEL LAYER (Entities)                        │
│  - SQLAlchemy models (31 models)                                │
│  - Entity definitions                                           │
│  - Relationships (Many-to-Many)                                 │
│  - Database schema mapping                                      │
│                                                                 │
│  Files: backend/app/models/*.py                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   POSTGRESQL DATABASE                           │
│                     (29 tables)                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Flux de Données

**Requête GET** (lecture) :
```
Client → Router → Schema (validation) → Service (logic) → Repository (query) → Model → Database
                                                                                           ↓
Client ← Router ← Schema (serialize) ← Service ← Repository ← SQLAlchemy ← PostgreSQL ←───┘
```

**Requête POST** (création) :
```
Client → Router → Schema (validate) → Service (business rules) → Repository (insert) → Database
                     ↓                        ↓                         ↓
              ValidationError           BusinessError           IntegrityError
                     ↓                        ↓                         ↓
                  422 Unprocessable       400 Bad Request          409 Conflict
```

---

## Modèle de Données

### Entités Principales (14)

```
┌─────────────────────────────────────────────────────────────────┐
│                       ENTITÉS PRINCIPALES                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Publication - Publications scientifiques (articles, etc.)   │
│  2. Auteur - Chercheurs et scientifiques                        │
│  3. Organisation - Universités, entreprises, labs               │
│  4. Theme - Thématiques IA (NLP, CV, RL, etc.)                  │
│  5. Dataset - Datasets utilisés                                 │
│  6. Technologie - Technologies IA (PyTorch, etc.)               │
│  7. Outil - Outils développement                                │
│  8. Source - Sources données (arXiv, etc.)                      │
│  9. Licence - Licences open source                              │
│ 10. Evenement - Conférences (NeurIPS, etc.)                     │
│ 11. ImpactSocietal - Impacts société                            │
│ 12. AuteurMetrique - Métriques auteur (h-index)                 │
│ 13. MetriqueEngagement - Engagement publications                │
│ 14. ChangementMetadonnees - Historique modif                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Relations Many-to-Many (17 tables association)

```
Publication ◄────────► Auteur (publication_auteur)
Publication ◄────────► Theme (publication_theme) *avec score confiance
Publication ◄────────► Dataset (publication_dataset)
Publication ◄────────► Technologie (publication_technologie)
Publication ◄────────► Outil (publication_outil)
Publication ◄────────► ImpactSocietal (publication_impact)
Publication ◄────────► MetriqueEngagement (publication_metrique)
Publication ◄────────► Publication (citation) *graph citations
Auteur ◄────────► Organisation (affiliation) *avec période
Auteur ◄────────► Collaboration (collaboration_auteur)
Organisation ◄────────► Collaboration (organisation_collaboration)
Technologie ◄────────► Dataset (technologie_dataset)
Technologie ◄────────► Outil (technologie_outil)
```

### Schéma Principal Publication

```sql
CREATE TABLE publication (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titre VARCHAR(500) NOT NULL,
    abstract TEXT,
    doi VARCHAR(255) UNIQUE,              -- Phase 3: Semantic Scholar enrichment
    arxiv_id VARCHAR(50) UNIQUE,          -- Phase 3: arXiv collection
    url TEXT,
    date_publication DATE,
    type_publication VARCHAR(50),         -- article, conference, preprint
    status VARCHAR(50) DEFAULT 'pending_enrichment',  -- Phase 3: tracking
    nb_citations INTEGER DEFAULT 0,
    metadata_ JSONB,                      -- Phase 3: flexible metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_publication_doi ON publication(doi);
CREATE INDEX idx_publication_arxiv_id ON publication(arxiv_id);
CREATE INDEX idx_publication_status ON publication(status);
CREATE INDEX idx_publication_date ON publication(date_publication);
```

### Champs Critiques Phase 3

| Table | Champ | Type | Usage Phase 3 |
|-------|-------|------|---------------|
| **publication** | `doi` | String(255) | Enrichissement Semantic Scholar API |
| **publication** | `arxiv_id` | String(50) | Pipeline collecte arXiv quotidien |
| **publication** | `status` | Enum | Tracking enrichissement (pending → enriched → failed) |
| **publication** | `metadata_` | JSONB | Stockage métadonnées brutes (flexible) |
| **auteur** | `h_index` | Integer | Métrique impact chercheur |
| **auteur** | `semantic_scholar_id` | String(50) | Liaison API Semantic Scholar |
| **auteur** | `orcid` | String(19) | Identifiant chercheur global |
| **publication_theme** | `score_confiance` | Float | Output ZeroShot classifier (0-1) |
| **publication_theme** | `est_principal` | Boolean | Thème primaire vs secondaire |

---

## API REST

### Structure API

```
/api                           # Base API
├── /health                   # Health check (DB + Redis)
├── /version                  # API version
└── /v1                       # API v1
    ├── /publications         # Publications CRUD
    ├── /auteurs              # Auteurs CRUD
    ├── /organisations        # Organisations CRUD
    ├── /themes               # Themes CRUD
    └── /datasets             # Datasets CRUD
```

### Endpoints par Ressource

Chaque ressource expose 5 endpoints REST standard :

```
GET    /api/v1/{resource}         - Liste avec pagination (skip, limit)
GET    /api/v1/{resource}/{id}    - Détail par UUID
POST   /api/v1/{resource}         - Création (Body JSON)
PUT    /api/v1/{resource}/{id}    - Mise à jour partielle (Body JSON)
DELETE /api/v1/{resource}/{id}    - Suppression
```

### Codes HTTP

| Code | Description | Usage |
|------|-------------|-------|
| **200** | OK | GET, PUT réussis |
| **201** | Created | POST réussi |
| **204** | No Content | DELETE réussi |
| **400** | Bad Request | Business rule violation |
| **404** | Not Found | Ressource inexistante |
| **422** | Unprocessable Entity | Validation Pydantic échouée |
| **500** | Internal Server Error | Erreur serveur |

### Exemple Requête/Réponse

**POST /api/v1/publications** (Créer publication)

Request:
```json
{
  "titre": "Deep Learning for AI Research",
  "abstract": "A comprehensive study on deep learning techniques",
  "doi": "10.1234/example.2025",
  "arxiv_id": "arxiv:2501.12345",
  "date_publication": "2025-11-17",
  "type_publication": "article",
  "status": "pending_enrichment"
}
```

Response (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "titre": "Deep Learning for AI Research",
  "abstract": "A comprehensive study on deep learning techniques",
  "doi": "10.1234/example.2025",
  "arxiv_id": "arxiv:2501.12345",
  "url": null,
  "date_publication": "2025-11-17",
  "type_publication": "article",
  "status": "pending_enrichment",
  "nb_citations": 0,
  "metadata_": null,
  "created_at": "2025-11-17T10:30:00Z",
  "updated_at": "2025-11-17T10:30:00Z"
}
```

### Pagination

Tous les endpoints GET liste supportent pagination :

```bash
GET /api/v1/publications?skip=0&limit=10
```

Paramètres :
- `skip` : Nombre items à ignorer (default: 0)
- `limit` : Nombre items max retournés (default: 100, max: 1000)

### Filtres (Phase 3)

Filtres additionnels par ressource :

**Publications** :
- `?status=pending_enrichment`
- `?type_publication=article`
- `?date_from=2025-01-01&date_to=2025-12-31`

**Auteurs** :
- `?organisation_id={uuid}`
- `?h_index_min=10`

**Organisations** :
- `?pays=France`
- `?type=university`

---

## Pipeline de Développement

### Workflow Git

```
main                    ← Production-ready code
 ├── feat/phase-3-etl   ← Feature branches
 ├── fix/bug-xyz        ← Bugfix branches
 └── docs/update-readme ← Documentation branches
```

**Commits atomiques** : 1 commit = 1 feature/étape complète avec tests

### CI/CD (Phase 3)

```
┌─────────────┐
│ Git Push    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         GitHub Actions CI               │
├─────────────────────────────────────────┤
│ 1. Linting (black, pylint)              │
│ 2. Type checking (mypy)                 │
│ 3. Tests (pytest)                       │
│ 4. Coverage report (>75%)               │
│ 5. Build Docker image                   │
│ 6. Security scan (bandit)               │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────┐
│ Merge main  │ ← Si tous checks OK
└─────────────┘
```

### Tests

**Stratégie TDD** : Tests avant implémentation

```
backend/tests/
├── repositories/          # 62 tests unitaires (94% coverage)
│   ├── test_base_repository.py
│   ├── test_publication_repository.py
│   ├── test_auteur_repository.py
│   ├── test_organisation_repository.py
│   └── test_theme_repository.py
├── services/              # 46 tests unitaires (86% coverage)
│   ├── test_publication_service.py
│   ├── test_auteur_service.py
│   ├── test_organisation_service.py
│   └── test_theme_service.py
└── api/                   # 70 tests intégration (68% coverage)
    ├── test_publications_api.py
    ├── test_auteurs_api.py
    ├── test_organisations_api.py
    ├── test_themes_api.py
    └── test_datasets_api.py
```

**Fixtures pytest** :
- `async_session` : Session DB test avec rollback
- `test_client` : Client FastAPI test (httpx)
- Factories : `create_publication()`, `create_auteur()`, etc.

**Commandes** :
```bash
# Tous tests
docker-compose exec api pytest tests/ -v

# Avec coverage
docker-compose exec api pytest tests/ --cov=app --cov-report=html

# Tests spécifiques
docker-compose exec api pytest tests/repositories/ -v
```

---

## Patterns & Principes

### 1. Repository Pattern

**Objectif** : Abstraire l'accès aux données, isoler logique DB

**Implémentation** :
```python
# backend/app/repositories/base_repository.py
class BaseRepository(Generic[T]):
    """Repository générique avec CRUD"""

    async def create(self, obj: T) -> T:
        """Créer entité"""

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Récupérer par ID"""

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Lister avec pagination"""

    async def update(self, id: UUID, data: dict) -> Optional[T]:
        """Mettre à jour"""

    async def delete(self, id: UUID) -> bool:
        """Supprimer"""
```

**Avantages** :
- Testabilité (mocks faciles)
- Réutilisabilité (BaseRepository)
- Changement DB facilité

### 2. Service Layer Pattern

**Objectif** : Encapsuler logique métier, orchestrer repositories

**Implémentation** :
```python
# backend/app/services/publication_service.py
class PublicationService:
    """Service publications avec logique métier"""

    def __init__(self,
                 publication_repo: PublicationRepository,
                 auteur_repo: AuteurRepository,
                 theme_repo: ThemeRepository):
        self.publication_repo = publication_repo
        self.auteur_repo = auteur_repo
        self.theme_repo = theme_repo

    async def create_publication_with_authors(
        self,
        publication_data: dict,
        author_ids: List[UUID]
    ) -> Publication:
        """Créer publication + associations auteurs"""
        # Validation business rules
        # Orchestration multi-repositories
        # Transaction management
```

**Avantages** :
- Logique métier centralisée
- Orchestration complexe
- Validation business rules

### 3. Dependency Injection

**Objectif** : Inverser dépendances, faciliter tests

**Implémentation FastAPI** :
```python
# backend/app/core/dependencies.py
async def get_db_session():
    """Dependency: session DB"""
    async with async_session_maker() as session:
        yield session

def get_publication_service(
    session: AsyncSession = Depends(get_db_session)
) -> PublicationService:
    """Dependency: service publications"""
    repo = PublicationRepository(session)
    return PublicationService(repo)

# backend/app/api/v1/publications.py
@router.post("/", response_model=PublicationResponse, status_code=201)
async def create_publication(
    data: PublicationCreate,
    service: PublicationService = Depends(get_publication_service)
):
    """Endpoint: créer publication"""
    return await service.create(data)
```

**Avantages** :
- Tests faciles (inject mocks)
- Couplage faible
- Réutilisabilité

### 4. DTO (Data Transfer Object) Pattern

**Objectif** : Valider/sérialiser données API

**Implémentation Pydantic** :
```python
# backend/app/schemas/publication.py
class PublicationCreate(BaseModel):
    """Schema création publication"""
    titre: str = Field(..., min_length=1, max_length=500)
    abstract: Optional[str] = None
    doi: Optional[str] = Field(None, pattern=r'^10\.\d{4,}/.*$')
    arxiv_id: Optional[str] = None
    date_publication: Optional[date] = None
    type_publication: Optional[str] = None

    @field_validator('doi')
    def validate_doi(cls, v):
        """Valider format DOI"""
        if v and not v.startswith('10.'):
            raise ValueError('DOI doit commencer par 10.')
        return v

class PublicationResponse(BaseModel):
    """Schema réponse publication"""
    id: UUID
    titre: str
    doi: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Avantages** :
- Validation automatique
- Documentation Swagger auto
- Type safety

---

## Décisions Architecturales

### ADR-001: PostgreSQL vs MongoDB

**Décision** : PostgreSQL
**Raison** :
- Relations complexes Many-to-Many
- ACID transactions requises
- Requêtes complexes (joins)
- Extensions (pg_trgm, pgvector Phase 3)

**Alternatives considérées** : MongoDB (rejeté : relations complexes)

### ADR-002: SQLAlchemy 2.0 Async

**Décision** : SQLAlchemy 2.0 avec async/await
**Raison** :
- Performance I/O async (concurrent requests)
- Compatibilité FastAPI async
- ORM mature et stable

**Alternatives considérées** : Tortoise ORM (rejeté : communauté plus petite)

### ADR-003: Layered Architecture

**Décision** : Architecture 5 layers (Router → Schema → Service → Repository → Model)
**Raison** :
- Separation of Concerns
- Testabilité élevée
- Maintenabilité long-terme

**Alternatives considérées** : MVC (rejeté : moins adapté API REST)

### ADR-004: UUID vs Auto-increment ID

**Décision** : UUID (gen_random_uuid())
**Raison** :
- Distribution (sharding futur)
- Sécurité (pas d'énumération)
- Compatibilité microservices

**Alternatives considérées** : SERIAL (rejeté : énumération possible)

### ADR-005: Pydantic 2.0

**Décision** : Pydantic 2.0 pour validation
**Raison** :
- Performance (Rust core)
- Type safety complète
- Swagger auto-documentation

**Alternatives considérées** : Marshmallow (rejeté : moins performant)

---

## Évolution Architecture

### Phase 1 → Phase 2 : Backend Complete ✅

**Ajouts Phase 2** :
- 31 modèles SQLAlchemy (14 entités + 17 associations)
- 29 tables PostgreSQL migrées
- 6 repositories (Data Access Layer)
- 5 services (Business Logic Layer)
- 24 schémas Pydantic
- 6 routers FastAPI (27 endpoints)
- 178 tests (100% passing)

**Architecture stable** : Layered architecture validée

### Phase 2 → Phase 3 : Pipeline ETL + ML 🔄

**Ajouts prévus Phase 3** :

```
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 3 ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              PIPELINE ETL (New)                        │    │
│  │  ┌──────────────────┐   ┌──────────────────┐          │    │
│  │  │ ArxivCollector   │   │ SemanticScholar  │          │    │
│  │  │ (Daily job)      │   │ Enricher         │          │    │
│  │  │ - Collect pubs   │   │ (Hourly job)     │          │    │
│  │  │ - Parse XML      │   │ - Enrich cites   │          │    │
│  │  │ - Deduplicate    │   │ - Update h-index │          │    │
│  │  └──────────────────┘   └──────────────────┘          │    │
│  │                                                        │    │
│  │  ┌──────────────────┐   ┌──────────────────┐          │    │
│  │  │ ZeroShot         │   │ Embeddings       │          │    │
│  │  │ Classifier       │   │ Extractor        │          │    │
│  │  │ (BART model)     │   │ (Sentence-Trans) │          │    │
│  │  └──────────────────┘   └──────────────────┘          │    │
│  │                                                        │    │
│  │  ┌──────────────────────────────────────────┐          │    │
│  │  │ APScheduler - Job Orchestration          │          │    │
│  │  │ - Daily: ArxivCollector (00:00 UTC)      │          │    │
│  │  │ - Hourly: SemanticScholar (every hour)   │          │    │
│  │  │ - Weekly: Metrics computation (Sunday)   │          │    │
│  │  └──────────────────────────────────────────┘          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              REDIS CACHE (Enhanced)                    │    │
│  │  - Publications cache (TTL 1h)                         │    │
│  │  - Authors cache (TTL 24h)                             │    │
│  │  - Classifications cache (TTL 7d)                      │    │
│  │  - Embeddings cache (TTL 30d)                          │    │
│  │  - Hit rate target: ≥80%                               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                MONITORING (New)                        │    │
│  │  - Structured logs (JSON)                              │    │
│  │  - APScheduler job monitoring                          │    │
│  │  - API performance metrics                             │    │
│  │  - Error alerting                                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Nouveaux composants** :
1. **ArxivCollector** - Pipeline collecte quotidienne arXiv
2. **SemanticScholarEnricher** - Enrichissement horaire citations/h-index
3. **ZeroShotClassifier** - Classification thématique BART
4. **EmbeddingsExtractor** - Extraction embeddings pour recherche sémantique
5. **APScheduler** - Orchestration jobs (daily, hourly, weekly)
6. **Redis Cache** - Cache avancé avec TTL différenciés
7. **Monitoring** - Logs structurés, métriques, alertes

**Impact architecture** :
- Ajout layer "Pipeline" entre Service et Database
- Redis passe de "ready" à "active" avec stratégie cache
- Ajout jobs asynchrones (APScheduler)

### Phase 3 → Phase 4 : Frontend + Deployment 📅

**Ajouts prévus Phase 4** :
- Frontend React 18 + TypeScript
- Visualisations (D3.js, Chart.js)
- Authentification JWT
- Rate limiting API
- Déploiement production (Docker Swarm / Kubernetes)
- CI/CD complet (GitHub Actions)

---

## 📊 Métriques Architecture

### Performance

| Métrique | Phase 2 (Actuel) | Phase 3 (Cible) |
|----------|------------------|-----------------|
| Response time API | ~150ms | <200ms |
| DB queries/sec | ~100 | ~500 |
| Concurrent users | ~10 | ~100 |
| Cache hit rate | 0% (no cache) | ≥80% |

### Scalabilité

| Métrique | Phase 2 | Phase 3 | Phase 4 |
|----------|---------|---------|---------|
| Publications | 0 | 15,000-25,000 | 100,000+ |
| Auteurs | 0 | 10,000-20,000 | 50,000+ |
| Requests/sec | ~10 | ~100 | ~1,000 |
| Storage | <100MB | ~5GB | ~50GB |

### Qualité Code

| Métrique | Valeur Actuelle |
|----------|----------------|
| Tests passing | 178/178 (100%) |
| Coverage | 68-94% |
| Lignes code backend | ~8,000 |
| Fichiers Python | 63 |
| Commits Git | 14 |

---

**Document généré le** : 17 Novembre 2025
**Architecture Version** : 2.0.0 (Phase 2 Complete)
**Prochaine version** : 3.0.0 (Phase 3 - ETL Pipeline)

---

*Fin du document ARCHITECTURE.md*
