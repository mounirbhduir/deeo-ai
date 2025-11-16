"""
Fixtures pytest pour tests des repositories

Fournit :
- async_session : Session DB de test asynchrone
- Fixtures de données de test pour chaque entité
- Nettoyage automatique entre tests
"""
import asyncio
from typing import AsyncGenerator
from datetime import date, datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.models import Base
from app.models.enums import (
    TypePublicationEnum,
    StatusPublicationEnum,
    TypeOrganisationEnum,
)


# URL de test (sera configurée via variable d'environnement en production)
TEST_DATABASE_URL = "postgresql+asyncpg://deeo_user:deeo_secure_password_2025@postgres:5432/deeo_ai_test"

# Configure pytest-asyncio to use auto mode
@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture pour session DB asynchrone de test.
    
    - Crée toutes les tables au début
    - Fournit une session pour le test
    - Rollback automatique après chaque test (isolation)
    - Nettoie les tables à la fin
    
    Yields:
        AsyncSession: Session de base de données de test
        
    Example:
        >>> async def test_something(async_session):
        ...     repository = PublicationRepository(async_session)
        ...     result = await repository.create({"titre": "Test"})
        ...     assert result.id is not None
    """
    # Create async engine with NullPool for testing
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Provide session to test
    async with async_session_factory() as session:
        yield session
        await session.rollback()
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


# ===== Fixtures de données de test =====

@pytest.fixture
def publication_data() -> dict:
    """
    Données de test pour créer une publication.
    
    Returns:
        Dictionnaire avec données valides pour Publication
    """
    return {
        "titre": "Attention Is All You Need",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
        "doi": f"10.1234/test.{uuid4().hex[:8]}",
        "arxiv_id": f"1706.{uuid4().int % 10000:05d}",
        "date_publication": date(2017, 6, 12),
        "type_publication": TypePublicationEnum.CONFERENCE_PAPER,
        "status": StatusPublicationEnum.PUBLISHED,
        "language": "en",
        "source_nom": "arXiv",
        "nombre_citations": 50000,
        "nombre_auteurs": 8,
        "score_popularite": 99.9,
    }


@pytest.fixture
def auteur_data() -> dict:
    """
    Données de test pour créer un auteur.
    
    Returns:
        Dictionnaire avec données valides pour Auteur
    """
    unique_id = uuid4().hex[:8]
    return {
        "nom": "Vaswani",
        "prenom": "Ashish",
        "email": f"test.{unique_id}@example.com",
        "orcid": f"0000-0002-{uuid4().int % 10000:04d}-{uuid4().int % 10000:04d}",
        "google_scholar_id": f"scholar_{unique_id}",
        "semantic_scholar_id": f"ss_{unique_id}",
        "homepage_url": "https://example.com/ashish",
        "h_index": 75,
        "nombre_publications": 50,
        "nombre_citations": 100000,
    }


@pytest.fixture
def organisation_data() -> dict:
    """
    Données de test pour créer une organisation.
    
    Returns:
        Dictionnaire avec données valides pour Organisation
    """
    return {
        "nom": "Google Research",
        "nom_court": "Google",
        "type_organisation": TypeOrganisationEnum.COMPANY,
        "pays": "USA",
        "ville": "Mountain View",
        "secteur": "Technology",
        "url": "https://research.google",
        "ranking_mondial": 5,
        "nombre_publications": 10000,
        "nombre_chercheurs": 500,
    }


@pytest.fixture
def theme_data() -> dict:
    """
    Données de test pour créer un thème.
    
    Returns:
        Dictionnaire avec données valides pour Theme
    """
    return {
        "label": "Machine Learning",
        "description": "Apprentissage automatique et algorithmes d'IA",
        "niveau_hierarchie": 1,
        "parent_id": None,
        "chemin_hierarchie": "Artificial Intelligence/Machine Learning",
        "nombre_publications": 50000,
    }


@pytest.fixture
def publication_minimal_data() -> dict:
    """
    Données minimales pour créer une publication (champs obligatoires seulement).
    
    Returns:
        Dictionnaire avec données minimales pour Publication
    """
    return {
        "titre": "Test Publication",
        "date_publication": date.today(),
        "type_publication": TypePublicationEnum.ARTICLE,
        "status": StatusPublicationEnum.PUBLISHED,
    }


@pytest.fixture
def auteur_minimal_data() -> dict:
    """
    Données minimales pour créer un auteur (champs obligatoires seulement).
    
    Returns:
        Dictionnaire avec données minimales pour Auteur
    """
    return {
        "nom": "Test",
    }


@pytest.fixture
def organisation_minimal_data() -> dict:
    """
    Données minimales pour créer une organisation (champs obligatoires seulement).
    
    Returns:
        Dictionnaire avec données minimales pour Organisation
    """
    return {
        "nom": "Test Organization",
        "type_organisation": TypeOrganisationEnum.UNIVERSITY,
    }


@pytest.fixture
def theme_minimal_data() -> dict:
    """
    Données minimales pour créer un thème (champs obligatoires seulement).
    
    Returns:
        Dictionnaire avec données minimales pour Theme
    """
    return {
        "label": "Test Theme",
        "niveau_hierarchie": 0,
    }


# ===== Fixtures d'instances créées en DB =====

@pytest_asyncio.fixture
async def created_publication(async_session: AsyncSession, publication_data: dict):
    """
    Fixture qui crée une publication en DB et la retourne.
    
    Args:
        async_session: Session DB de test
        publication_data: Données de publication
        
    Returns:
        Publication créée en DB
    """
    from app.repositories import PublicationRepository
    
    repository = PublicationRepository(async_session)
    publication = await repository.create(publication_data)
    return publication


@pytest_asyncio.fixture
async def created_auteur(async_session: AsyncSession, auteur_data: dict):
    """
    Fixture qui crée un auteur en DB et le retourne.
    
    Args:
        async_session: Session DB de test
        auteur_data: Données d'auteur
        
    Returns:
        Auteur créé en DB
    """
    from app.repositories import AuteurRepository
    
    repository = AuteurRepository(async_session)
    auteur = await repository.create(auteur_data)
    return auteur


@pytest_asyncio.fixture
async def created_organisation(async_session: AsyncSession, organisation_data: dict):
    """
    Fixture qui crée une organisation en DB et la retourne.
    
    Args:
        async_session: Session DB de test
        organisation_data: Données d'organisation
        
    Returns:
        Organisation créée en DB
    """
    from app.repositories import OrganisationRepository
    
    repository = OrganisationRepository(async_session)
    organisation = await repository.create(organisation_data)
    return organisation


@pytest_asyncio.fixture
async def created_theme(async_session: AsyncSession, theme_data: dict):
    """
    Fixture qui crée un thème en DB et le retourne.
    
    Args:
        async_session: Session DB de test
        theme_data: Données de thème
        
    Returns:
        Theme créé en DB
    """
    from app.repositories import ThemeRepository
    
    repository = ThemeRepository(async_session)
    theme = await repository.create(theme_data)
    return theme
