"""Tests for Enrichment Service.

Test coverage:
- Service initialization
- Single publication enrichment
- Batch enrichment
- Database updates
- Author matching
- Error handling
- Statistics calculation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.enrichment.enrichment_service import (
    EnrichmentService,
    EnrichmentStats,
    EnrichmentError,
)
from app.models.publication import Publication
from app.models.auteur import Auteur
from app.models.publication_auteur import PublicationAuteur


@pytest.fixture
def mock_publication():
    """Create mock publication."""
    pub = Publication(
        id=uuid.uuid4(),
        titre="Test Paper",
        abstract="Test abstract",
        arxiv_id="2401.12345",
        doi="10.1234/test",
        date_publication=date(2024, 1, 15),
        type_publication="article",
        status="published",
        nombre_citations=0,
        nombre_auteurs=2,
    )
    return pub


@pytest.fixture
def mock_auteur():
    """Create mock author."""
    author = Auteur(
        id=uuid.uuid4(),
        nom="Doe",
        prenom="John",
        h_index=0,
        nombre_publications=0,
        nombre_citations=0,
    )
    return author


@pytest.fixture
def mock_enrichment_data():
    """Mock enrichment data from Semantic Scholar."""
    return {
        "semantic_scholar_id": "test-s2-id",
        "citation_count": 42,
        "reference_count": 25,
        "influential_citation_count": 5,
        "venue": "ICML 2024",
        "publication_date": "2024-01-15",
        "fields_of_study": ["Computer Science", "Machine Learning"],
        "s2_fields_of_study": ["Computer Science", "Machine Learning"],
        "external_ids": {"ArXiv": "2401.12345"},
        "authors": [
            {
                "semantic_scholar_id": "author-1",
                "name": "John Doe",
                "h_index": None,
                "citation_count": None,
            }
        ],
        "enriched_at": datetime.now().isoformat(),
    }


class TestEnrichmentStats:
    """Tests for EnrichmentStats."""

    def test_stats_initialization(self):
        """Test stats initialization."""
        stats = EnrichmentStats()

        assert stats.total_publications == 0
        assert stats.enriched_publications == 0
        assert stats.failed_publications == 0
        assert stats.skipped_publications == 0
        assert stats.citations_updated == 0
        assert stats.start_time is None
        assert stats.end_time is None

    def test_stats_duration(self):
        """Test duration calculation."""
        stats = EnrichmentStats()
        stats.start_time = datetime(2024, 1, 1, 12, 0, 0)
        stats.end_time = datetime(2024, 1, 1, 12, 5, 30)

        assert stats.duration_seconds == 330.0  # 5 minutes 30 seconds

    def test_stats_to_dict(self):
        """Test converting stats to dictionary."""
        stats = EnrichmentStats()
        stats.total_publications = 10
        stats.enriched_publications = 8
        stats.failed_publications = 2

        result = stats.to_dict()

        assert result["total_publications"] == 10
        assert result["enriched_publications"] == 8
        assert result["failed_publications"] == 2


class TestEnrichmentService:
    """Tests for EnrichmentService."""

    @pytest.mark.asyncio
    async def test_service_initialization(self, async_session):
        """Test service initialization."""
        service = EnrichmentService(async_session)

        assert service.db == async_session
        assert service.api_key is None
        assert service.batch_size == 50
        assert service.max_concurrent == 5

    @pytest.mark.asyncio
    async def test_service_initialization_with_api_key(self, async_session):
        """Test service initialization with API key."""
        service = EnrichmentService(async_session, api_key="test-key")

        assert service.api_key == "test-key"

    @pytest.mark.asyncio
    async def test_service_context_manager(self, async_session):
        """Test service as async context manager."""
        async with EnrichmentService(async_session) as service:
            assert service.client is not None

    @pytest.mark.asyncio
    async def test_enrich_single_publication_success(
        self, async_session, mock_publication, mock_enrichment_data
    ):
        """Test enriching a single publication successfully."""
        async with EnrichmentService(async_session) as service:
            # Mock repository and client methods
            service.publication_repo.get_by_id = AsyncMock(return_value=mock_publication)
            service._fetch_semantic_scholar_data = AsyncMock(
                return_value=mock_enrichment_data
            )
            service._update_publication = AsyncMock()
            service._update_authors = AsyncMock()
            async_session.commit = AsyncMock()
            async_session.refresh = AsyncMock()

            result = await service.enrich_single_publication(str(mock_publication.id))

            assert result is not None
            assert result["citation_count"] == 42
            service._update_publication.assert_called_once()
            service._update_authors.assert_called_once()

    @pytest.mark.asyncio
    async def test_enrich_single_publication_not_found(self, async_session):
        """Test enriching publication that doesn't exist."""
        async with EnrichmentService(async_session) as service:
            service.publication_repo.get_by_id = AsyncMock(return_value=None)

            result = await service.enrich_single_publication(str(uuid.uuid4()))

            assert result is None

    @pytest.mark.asyncio
    async def test_enrich_single_publication_no_data(
        self, async_session, mock_publication
    ):
        """Test enriching publication with no Semantic Scholar data."""
        async with EnrichmentService(async_session) as service:
            service.publication_repo.get_by_id = AsyncMock(return_value=mock_publication)
            service._fetch_semantic_scholar_data = AsyncMock(return_value=None)

            result = await service.enrich_single_publication(str(mock_publication.id))

            assert result is None

    @pytest.mark.asyncio
    async def test_enrich_single_publication_error(
        self, async_session, mock_publication
    ):
        """Test error handling during enrichment."""
        async with EnrichmentService(async_session) as service:
            service.publication_repo.get_by_id = AsyncMock(return_value=mock_publication)
            service._fetch_semantic_scholar_data = AsyncMock(
                side_effect=Exception("API error")
            )
            async_session.rollback = AsyncMock()

            result = await service.enrich_single_publication(str(mock_publication.id))

            assert result is None
            async_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_publication(
        self, async_session, mock_publication, mock_enrichment_data
    ):
        """Test updating publication with enrichment data."""
        service = EnrichmentService(async_session)

        await service._update_publication(mock_publication, mock_enrichment_data)

        assert mock_publication.nombre_citations == 42
        assert mock_publication.source_nom == "ICML 2024"

    @pytest.mark.asyncio
    async def test_match_author_name(self, async_session, mock_auteur):
        """Test author name matching."""
        service = EnrichmentService(async_session)

        # Exact match
        assert service._match_author_name(mock_auteur, "John Doe")

        # Last name match
        assert service._match_author_name(mock_auteur, "J. Doe")

        # No match
        assert not service._match_author_name(mock_auteur, "Jane Smith")

    @pytest.mark.asyncio
    async def test_update_authors(
        self, async_session, mock_publication, mock_auteur, mock_enrichment_data
    ):
        """Test updating authors with enrichment data."""
        # Setup publication with authors
        pub_author = PublicationAuteur(
            publication_id=mock_publication.id,
            auteur_id=mock_auteur.id,
            ordre=1,
        )
        pub_author.auteur = mock_auteur
        mock_publication.auteurs = [pub_author]

        service = EnrichmentService(async_session)
        async_session.refresh = AsyncMock()

        await service._update_authors(mock_publication, mock_enrichment_data)

        # Should update Semantic Scholar ID
        assert mock_auteur.semantic_scholar_id == "author-1"

    @pytest.mark.asyncio
    async def test_get_publications_to_enrich(self, async_session, mock_publication):
        """Test getting publications that need enrichment."""
        service = EnrichmentService(async_session)

        # Mock database query
        with patch.object(async_session, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_publication]
            mock_execute.return_value = mock_result

            publications = await service._get_publications_to_enrich(None, False)

            assert len(publications) == 1
            assert publications[0] == mock_publication

    @pytest.mark.asyncio
    async def test_get_publications_to_enrich_with_ids(
        self, async_session, mock_publication
    ):
        """Test getting specific publications."""
        service = EnrichmentService(async_session)

        pub_ids = [str(mock_publication.id)]

        with patch.object(async_session, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [mock_publication]
            mock_execute.return_value = mock_result

            publications = await service._get_publications_to_enrich(pub_ids, False)

            assert len(publications) == 1

    @pytest.mark.asyncio
    async def test_enrich_batch(self, async_session, mock_publication):
        """Test batch enrichment."""
        async with EnrichmentService(async_session) as service:
            service.enrich_single_publication = AsyncMock(
                return_value={"citation_count": 42}
            )

            publications = [mock_publication, mock_publication]
            stats = await service._enrich_batch(publications)

            assert stats["enriched"] == 2
            assert stats["failed"] == 0
            assert stats["citations_updated"] == 84  # 42 * 2

    @pytest.mark.asyncio
    async def test_enrich_batch_with_failures(self, async_session, mock_publication):
        """Test batch enrichment with some failures."""
        async with EnrichmentService(async_session) as service:
            # First succeeds, second fails, third returns None
            service.enrich_single_publication = AsyncMock(
                side_effect=[
                    {"citation_count": 42},
                    Exception("Error"),
                    None,
                ]
            )

            publications = [mock_publication, mock_publication, mock_publication]
            stats = await service._enrich_batch(publications)

            assert stats["enriched"] == 1
            assert stats["failed"] == 1
            assert stats["skipped"] == 1

    @pytest.mark.asyncio
    async def test_get_enrichment_stats(self, async_session, mock_publication):
        """Test getting enrichment statistics."""
        # Setup publications with different citation counts
        mock_publication.nombre_citations = 10

        service = EnrichmentService(async_session)

        with patch.object(async_session, 'execute') as mock_execute:
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = [
                mock_publication,
                mock_publication,
            ]
            mock_execute.return_value = mock_result

            stats = await service.get_enrichment_stats_for_publications()

            assert stats["total_publications"] == 2
            assert stats["enriched_publications"] == 2
            assert stats["total_citations"] == 20
            assert stats["average_citations"] == 10.0

    @pytest.mark.asyncio
    async def test_fetch_semantic_scholar_data_arxiv(
        self, async_session, mock_publication, mock_enrichment_data
    ):
        """Test fetching data by arXiv ID."""
        async with EnrichmentService(async_session) as service:
            service.client.get_paper_by_arxiv_id = AsyncMock(
                return_value={"paperId": "test"}
            )
            service.client.extract_enrichment_data = MagicMock(
                return_value=mock_enrichment_data
            )

            result = await service._fetch_semantic_scholar_data(mock_publication)

            assert result == mock_enrichment_data
            service.client.get_paper_by_arxiv_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_semantic_scholar_data_doi_fallback(
        self, async_session, mock_publication, mock_enrichment_data
    ):
        """Test falling back to DOI when arXiv fails."""
        mock_publication.arxiv_id = None

        async with EnrichmentService(async_session) as service:
            service.client.get_paper_by_doi = AsyncMock(
                return_value={"paperId": "test"}
            )
            service.client.extract_enrichment_data = MagicMock(
                return_value=mock_enrichment_data
            )

            result = await service._fetch_semantic_scholar_data(mock_publication)

            assert result == mock_enrichment_data
            service.client.get_paper_by_doi.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_semantic_scholar_data_not_found(
        self, async_session, mock_publication
    ):
        """Test handling paper not found."""
        async with EnrichmentService(async_session) as service:
            service.client.get_paper_by_arxiv_id = AsyncMock(return_value=None)
            service.client.get_paper_by_doi = AsyncMock(return_value=None)

            result = await service._fetch_semantic_scholar_data(mock_publication)

            assert result is None
