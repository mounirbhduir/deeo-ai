"""Fixtures for services tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.models.publication import Publication
from app.models.auteur import Auteur
from app.models.organisation import Organisation
from app.models.theme import Theme


@pytest.fixture
def mock_db_session():
    """Create a mock async database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def sample_publication_data():
    """Sample publication data for testing."""
    return {
        "titre": "Test Publication",
        "abstract": "This is a test abstract",
        "doi": "10.1234/test.2024.001",
        "arxiv_id": "2024.12345",
        "date_publication": datetime(2024, 1, 1),
        "type_publication": "article",
        "status": "pending_enrichment"
    }


@pytest.fixture
def sample_publication():
    """Sample publication instance for testing."""
    pub = Publication(
        titre="Test Publication",
        abstract="This is a test abstract",
        doi="10.1234/test.2024.001",
        arxiv_id="2024.12345",
        date_publication=datetime(2024, 1, 1),
        type_publication="article",
        status="pending_enrichment",
        nombre_citations=10
    )
    pub.id = 1
    return pub


@pytest.fixture
def sample_auteur_data():
    """Sample auteur data for testing."""
    return {
        "nom": "Doe",
        "prenom": "John",
        "email": "john.doe@example.com",
        "orcid": "0000-0001-2345-6789",
        "h_index": 25
    }


@pytest.fixture
def sample_auteur():
    """Sample auteur instance for testing."""
    auteur = Auteur(
        nom="Doe",
        prenom="John",
        email="john.doe@example.com",
        orcid="0000-0001-2345-6789",
        h_index=25,
        nombre_publications=50,
        nombre_citations=500
    )
    auteur.id = 1
    return auteur


@pytest.fixture
def sample_organisation_data():
    """Sample organisation data for testing."""
    return {
        "nom": "Test University",
        "nom_court": "TU",
        "type_organisation": "university",
        "pays": "USA",
        "ville": "New York"
    }


@pytest.fixture
def sample_organisation():
    """Sample organisation instance for testing."""
    org = Organisation(
        nom="Test University",
        nom_court="TU",
        type_organisation="university",
        pays="USA",
        ville="New York",
        nombre_publications=100,
        nombre_chercheurs=50
    )
    org.id = 1
    return org


@pytest.fixture
def sample_theme_data():
    """Sample theme data for testing."""
    return {
        "label": "Machine Learning",
        "description": "AI subfield focused on learning from data",
        "niveau_hierarchie": 1,
        "parent_id": None
    }


@pytest.fixture
def sample_theme():
    """Sample theme instance for testing."""
    theme = Theme(
        label="Machine Learning",
        description="AI subfield focused on learning from data",
        niveau_hierarchie=1,
        parent_id=None,
        nombre_publications=200
    )
    theme.id = 1
    return theme
