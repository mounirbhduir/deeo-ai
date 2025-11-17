"""Tests for deduplication service."""

import pytest
from datetime import date
from unittest.mock import AsyncMock, Mock

from app.pipelines.deduplication import DeduplicationService
from app.models.publication import Publication


@pytest.fixture
def dedup_service():
    """Create deduplication service instance."""
    return DeduplicationService(title_similarity_threshold=0.95)


@pytest.mark.asyncio
class TestDeduplicationService:
    """Test suite for DeduplicationService."""

    async def test_initialization(self, dedup_service):
        """Test service initialization."""
        assert dedup_service.title_similarity_threshold == 0.95

    async def test_find_duplicate_by_doi(self, dedup_service, async_session):
        """Test finding duplicate by DOI."""
        # Create existing publication
        existing = Publication(
            titre="Test Paper",
            doi="10.1234/test",
            abstract="Abstract",
            date_publication=date.today(),
            type_publication='preprint',
        )
        async_session.add(existing)
        await async_session.commit()

        # Search for duplicate
        new_data = {
            'doi': '10.1234/test',
            'titre': 'Different Title',
        }

        duplicate = await dedup_service.find_duplicate(async_session, new_data)

        assert duplicate is not None
        assert duplicate.id == existing.id

    async def test_find_duplicate_by_arxiv_id(self, dedup_service, async_session):
        """Test finding duplicate by arXiv ID."""
        # Create existing publication
        existing = Publication(
            titre="Test Paper",
            arxiv_id="2311.12345",
            abstract="Abstract",
            date_publication=date.today(),
            type_publication='preprint',
        )
        async_session.add(existing)
        await async_session.commit()

        # Search for duplicate
        new_data = {
            'arxiv_id': '2311.12345',
            'titre': 'Different Title',
        }

        duplicate = await dedup_service.find_duplicate(async_session, new_data)

        assert duplicate is not None
        assert duplicate.id == existing.id

    async def test_find_duplicate_by_title_similarity(self, dedup_service, async_session):
        """Test finding duplicate by title similarity."""
        # Create existing publication
        existing = Publication(
            titre="Attention is All You Need",
            abstract="Abstract",
            date_publication=date.today(),
            type_publication='preprint',
        )
        async_session.add(existing)
        await async_session.commit()

        # Search for duplicate with similar title
        new_data = {
            'titre': 'Attention Is All You Need',  # Same but different case
        }

        duplicate = await dedup_service.find_duplicate(async_session, new_data)

        assert duplicate is not None
        assert duplicate.id == existing.id

    async def test_find_duplicate_no_match(self, dedup_service, async_session):
        """Test no duplicate found."""
        # Create existing publication
        existing = Publication(
            titre="Different Paper",
            doi="10.1234/different",
            abstract="Abstract",
            date_publication=date.today(),
            type_publication='preprint',
        )
        async_session.add(existing)
        await async_session.commit()

        # Search for duplicate
        new_data = {
            'doi': '10.5678/new',
            'titre': 'Completely Different Title',
        }

        duplicate = await dedup_service.find_duplicate(async_session, new_data)

        assert duplicate is None

    def test_calculate_similarity(self, dedup_service):
        """Test similarity calculation."""
        # Identical texts
        similarity = dedup_service._calculate_similarity(
            "Attention is all you need",
            "Attention is all you need"
        )
        assert similarity == 1.0

        # Same text, different case
        similarity = dedup_service._calculate_similarity(
            "Attention is All You Need",
            "attention is all you need"
        )
        assert similarity > 0.95

        # Different texts
        similarity = dedup_service._calculate_similarity(
            "Attention is all you need",
            "Deep learning fundamentals"
        )
        assert similarity < 0.5

    def test_should_update_more_citations(self, dedup_service):
        """Test should update when new data has more citations."""
        existing = Publication(titre="Test", nombre_citations=10, abstract="Abstract", date_publication=date.today(), type_publication='preprint')
        new_data = {'nombre_citations': 20}

        assert dedup_service.should_update(existing, new_data) is True

    def test_should_update_has_abstract(self, dedup_service):
        """Test should update when new data has abstract and existing doesn't."""
        existing = Publication(titre="Test", abstract=None, date_publication=date.today(), type_publication='preprint')
        new_data = {'abstract': 'New abstract'}

        assert dedup_service.should_update(existing, new_data) is True

    def test_should_update_no_reason(self, dedup_service):
        """Test should not update when no improvements."""
        existing = Publication(
            titre="Test",
            abstract="Abstract",
            nombre_citations=20,
            doi="10.1234/test",
            date_publication=date.today(),
            type_publication='preprint',
        )
        new_data = {
            'abstract': 'Different abstract',
            'nombre_citations': 10,
        }

        assert dedup_service.should_update(existing, new_data) is False

    async def test_merge_publications(self, dedup_service, async_session):
        """Test merging publications."""
        existing = Publication(
            titre="Test Paper",
            abstract=None,
            doi=None,
            nombre_citations=5,
            date_publication=date.today(),
            type_publication='preprint',
        )
        async_session.add(existing)
        await async_session.commit()

        new_data = {
            'abstract': 'New abstract',
            'doi': '10.1234/new',
            'nombre_citations': 10,
        }

        merged = await dedup_service.merge_publications(async_session, existing, new_data)

        assert merged.abstract == 'New abstract'
        assert merged.doi == '10.1234/new'
        assert merged.nombre_citations == 10
