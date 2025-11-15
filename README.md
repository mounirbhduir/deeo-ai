# DEEO.AI - Proof of Concept

**AI Dynamic Emergence and Evolution Observatory**

Open source observatory for tracking and analyzing AI technologies, publications, and actors.

---

## 🚀 Quick Start

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

4. **Verify services**
```bash
   # Check PostgreSQL
   docker-compose exec postgres pg_isready -U deeo_user
   
   # Check Redis
   docker-compose exec redis redis-cli ping
   
   # Check API
   curl http://localhost:8000/api/health
```

5. **Access API documentation**
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

---

## 📁 Project Structure
```
deeo-ai-poc/
├── backend/           # FastAPI application
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   └── tests/        # Tests
├── frontend/          # React application (Phase 4)
├── tests/             # Additional tests
├── scripts/           # Utility scripts
├── docs/              # Documentation
└── docker-compose.yml # Services orchestration
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
```

---

## 📊 API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/version` - API version

### Publications (Phase 2)
- `GET /api/v1/publications` - List publications
- `POST /api/v1/publications` - Create publication
- `GET /api/v1/publications/{id}` - Get publication details

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI 0.104, SQLAlchemy 2.0
- **Database**: PostgreSQL 15.5
- **Cache**: Redis 7
- **Frontend**: React 18, TypeScript 5 (Phase 4)
- **Infrastructure**: Docker, Docker Compose

---

## 📖 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/api/docs)

---

## ✅ Phase 1 Status

**Completed** : Setup Projet et Infrastructure
- ✅ Docker Compose (PostgreSQL 15.5 + Redis 7 + FastAPI)
- ✅ FastAPI skeleton with health endpoints
- ✅ Alembic migrations configured
- ✅ Tests passing (79% coverage)
- ✅ Documentation

**Next** : Phase 2 - SQLAlchemy Models + API Base

---

## 📝 License

MIT License - See LICENSE file

---

## 👥 Authors

- Mounir - Master Big Data & IA - UIR

---

**Version**: 1.0.0 (Phase 1 - Setup)  
**Last Updated**: November 15, 2025