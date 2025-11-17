# DEEO.AI - Proof of Concept

[![Tests](https://img.shields.io/badge/tests-178%2F178%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-68--94%25-green)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.5-336791)]()
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D)]()

**AI Dynamic Emergence and Evolution Observatory**

Open source observatory for tracking and analyzing AI technologies, publications, and actors.

---

## 🎯 Phase 2 Complete ✅

**Phase 2 - Modèles SQLAlchemy + API CRUD** est maintenant **100% complétée** !

### Accomplissements Phase 2

- ✅ **31 modèles SQLAlchemy** créés (14 entités + 17 associations)
- ✅ **29 tables PostgreSQL** migrées avec Alembic
- ✅ **6 repositories** avec Data Access Layer (94% coverage)
- ✅ **5 services** avec Business Logic (86% coverage)
- ✅ **24 schémas Pydantic** avec validation
- ✅ **6 routers FastAPI** avec 27 endpoints REST
- ✅ **178 tests passing** (100% success rate) 🏆
- ✅ **Coverage 68-94%** selon layer
- ✅ **Swagger UI** auto-documentée
- ✅ **Architecture Layered** complète

**Prochaine étape** : Phase 3 - Pipeline ETL + ML Classification 🚀

---

## 🚀 Quick Start - Phase 2

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd deeo-ai-poc
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Run database migrations**
```bash
docker-compose exec api alembic upgrade head
```

5. **Verify services**
```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U deeo_user

# Check Redis
docker-compose exec redis redis-cli ping

# Check API
curl http://localhost:8000/api/health
```

6. **Access API documentation**
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

---

## 📚 API Endpoints (Phase 2)

### Health & Status
- `GET /` - Root endpoint
- `GET /api/health` - Health check (database + Redis)
- `GET /api/version` - API version

### Publications
- `GET /api/v1/publications` - List publications (pagination)
- `GET /api/v1/publications/{id}` - Get publication by ID
- `POST /api/v1/publications` - Create publication
- `PUT /api/v1/publications/{id}` - Update publication
- `DELETE /api/v1/publications/{id}` - Delete publication

### Auteurs
- `GET /api/v1/auteurs` - List authors (pagination)
- `GET /api/v1/auteurs/{id}` - Get author by ID
- `POST /api/v1/auteurs` - Create author
- `PUT /api/v1/auteurs/{id}` - Update author
- `DELETE /api/v1/auteurs/{id}` - Delete author

### Organisations
- `GET /api/v1/organisations` - List organizations (pagination)
- `GET /api/v1/organisations/{id}` - Get organization by ID
- `POST /api/v1/organisations` - Create organization
- `PUT /api/v1/organisations/{id}` - Update organization
- `DELETE /api/v1/organisations/{id}` - Delete organization

### Themes
- `GET /api/v1/themes` - List themes (pagination)
- `GET /api/v1/themes/{id}` - Get theme by ID
- `POST /api/v1/themes` - Create theme
- `PUT /api/v1/themes/{id}` - Update theme
- `DELETE /api/v1/themes/{id}` - Delete theme

### Datasets
- `GET /api/v1/datasets` - List datasets (pagination)
- `GET /api/v1/datasets/{id}` - Get dataset by ID
- `POST /api/v1/datasets` - Create dataset
- `PUT /api/v1/datasets/{id}` - Update dataset
- `DELETE /api/v1/datasets/{id}` - Delete dataset

### API Examples

**List publications with pagination:**
```bash
curl "http://localhost:8000/api/v1/publications?skip=0&limit=10"
```

**Get publication by ID:**
```bash
curl "http://localhost:8000/api/v1/publications/{uuid}"
```

**Create publication:**
```bash
curl -X POST "http://localhost:8000/api/v1/publications" \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "Deep Learning for AI Research",
    "abstract": "A comprehensive study on deep learning techniques",
    "doi": "10.1234/example.2025",
    "arxiv_id": "arxiv:2501.12345",
    "date_publication": "2025-11-17",
    "type_publication": "article",
    "status": "pending_enrichment"
  }'
```

**Update publication:**
```bash
curl -X PUT "http://localhost:8000/api/v1/publications/{uuid}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "enriched",
    "metadata_": {"citations_count": 42}
  }'
```

**Delete publication:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/publications/{uuid}"
```

---

## 🏗️ Project Structure (Phase 2)

```
deeo-ai-poc/
├── backend/                    # FastAPI application
│   ├── app/                   # Application code
│   │   ├── models/           # 31 SQLAlchemy models
│   │   ├── repositories/     # 6 repositories (Data Access Layer)
│   │   ├── services/         # 5 services (Business Logic)
│   │   ├── schemas/          # 24 Pydantic schemas
│   │   ├── api/              # 6 FastAPI routers
│   │   │   └── v1/          # API v1 endpoints
│   │   ├── core/            # Core utilities
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database setup
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   ├── tests/               # 178 tests (100% passing)
│   │   ├── repositories/   # 62 tests (94% coverage)
│   │   ├── services/       # 46 tests (86% coverage)
│   │   └── api/            # 70 tests (68% coverage)
│   ├── Dockerfile           # Docker image
│   ├── requirements.txt     # Python dependencies
│   ├── pytest.ini          # pytest configuration
│   └── conftest.py         # Test fixtures
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md      # Architecture technique
│   ├── MEMORY_BANK_PHASE_2_FINAL.md
│   ├── RAPPORT_PHASE_2_COMPLETE.md
│   └── context/            # Project context
├── frontend/                # React application (Phase 4)
├── tests/                   # Additional tests
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Services orchestration
├── .env.example             # Environment template
└── README.md                # This file
```

---

## 📊 Test Coverage (Phase 2)

| Layer | Tests | Coverage | Status |
|-------|-------|----------|--------|
| **Repositories** | 62 | 94% | ✅ Excellent |
| **Services** | 46 | 86% | ✅ Très bon |
| **API** | 70 | 68-74% | ✅ Bon |
| **Total** | **178** | **68-94%** | ✅ Solide |

**Run tests:**
```bash
# All tests
docker-compose exec api pytest tests/ -v

# With coverage
docker-compose exec api pytest tests/ --cov=app --cov-report=term-missing

# Coverage HTML report
docker-compose exec api pytest tests/ --cov=app --cov-report=html
# Open: backend/htmlcov/index.html

# Specific layer
docker-compose exec api pytest tests/repositories/ -v
docker-compose exec api pytest tests/services/ -v
docker-compose exec api pytest tests/api/ -v
```

---

## 🧪 Development

### Run tests
```bash
docker-compose exec api pytest -v
docker-compose exec api pytest --cov=app --cov-report=html
```

### Code quality
```bash
# Formatting
docker-compose exec api black app/

# Linting
docker-compose exec api pylint app/
```

### Database migrations
```bash
# Create migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1

# Migration history
docker-compose exec api alembic history
```

### Database access
```bash
# PostgreSQL shell
docker-compose exec postgres psql -U deeo_user -d deeo_ai

# List tables
docker-compose exec postgres psql -U deeo_user -d deeo_ai -c '\dt'

# View table structure
docker-compose exec postgres psql -U deeo_user -d deeo_ai -c '\d+ publication'

# Redis CLI
docker-compose exec redis redis-cli
```

---

## 🛠️ Tech Stack

### Backend
- **Python** 3.11+ - Language with type hints, async/await
- **FastAPI** 0.104+ - Modern async web framework
- **SQLAlchemy** 2.0 - Async ORM with PostgreSQL
- **Alembic** 1.12+ - Database migrations
- **Pydantic** 2.0+ - Data validation and schemas
- **pytest** 7.4+ - Testing framework with pytest-asyncio

### Infrastructure
- **PostgreSQL** 15.5 - Main database (29 tables)
- **Redis** 7.0 - Cache and sessions
- **Docker** - Containerization
- **Docker Compose** - Services orchestration

### Development Tools
- **Git** - Version control
- **Claude Code** - AI-powered development assistant

---

## 📖 Documentation

- [Architecture](docs/ARCHITECTURE.md) - Technical architecture details
- [Memory Bank Phase 2](docs/MEMORY_BANK_PHASE_2_FINAL.md) - Phase 2 complete state
- [Phase 2 Report](docs/RAPPORT_PHASE_2_COMPLETE.md) - Detailed Phase 2 report
- [API Documentation](http://localhost:8000/api/docs) - Swagger UI (when running)

---

## 🎯 Next Steps - Phase 3

**Phase 3 - Pipeline ETL + ML Classification** (Upcoming)

### Planned Features
1. **ArxivCollector** - Daily pipeline to collect publications from arXiv API
2. **SemanticScholarEnricher** - Hourly enrichment with citations, h-index, author metrics
3. **ZeroShotClassifier** - Multi-label theme classification with BART model
4. **EmbeddingsExtractor** - Semantic search with Sentence-Transformers
5. **APScheduler** - Job orchestration (daily, hourly, weekly jobs)
6. **Redis Cache** - Advanced caching with differentiated TTLs
7. **Monitoring** - Structured logs, job tracking, performance metrics
8. **Documentation** - ETL pipeline guides, configuration docs

### Expected Volumes
- 15,000-25,000 publications
- 10,000-20,000 authors
- 2,000-5,000 organizations
- 50-100 active themes
- 50,000-100,000 classifications

---

## ✅ Project Status

### Phase 1 - Infrastructure ✅ **COMPLETE**
- ✅ Docker Compose (PostgreSQL + Redis + FastAPI)
- ✅ FastAPI skeleton with health endpoints
- ✅ Alembic migrations configured
- ✅ Initial tests passing (79% coverage)

### Phase 2 - Backend + API ✅ **COMPLETE**
- ✅ 31 SQLAlchemy models + 29 PostgreSQL tables
- ✅ 6 repositories (94% coverage)
- ✅ 5 services (86% coverage)
- ✅ 24 Pydantic schemas
- ✅ 6 FastAPI routers + 27 REST endpoints
- ✅ 178 tests passing (100% success rate)
- ✅ Swagger UI documentation

### Phase 3 - ETL Pipeline + ML 🔄 **UPCOMING**
- [ ] ArxivCollector pipeline
- [ ] SemanticScholar enrichment
- [ ] ZeroShot classification
- [ ] Embeddings extraction
- [ ] APScheduler jobs
- [ ] Redis cache advanced
- [ ] Tests ≥80% coverage

### Phase 4 - Frontend + Deployment 📅 **PLANNED**
- [ ] React 18 + TypeScript frontend
- [ ] Interactive visualizations
- [ ] User authentication
- [ ] Production deployment

---

## 📝 License

MIT License - See LICENSE file

---

## 👥 Authors

**Mounir** - Master Big Data & IA - Université Internationale de Rabat (UIR)

---

## 🙏 Acknowledgments

- Developed with assistance from **Claude Code** (Anthropic)
- Phase 2 completed with "Claude Code First" workflow (91% time gain)

---

**Version**: 2.0.0 (Phase 2 - Backend Complete)
**Last Updated**: November 17, 2025
**Status**: ✅ Phase 2 Complete - Ready for Phase 3
