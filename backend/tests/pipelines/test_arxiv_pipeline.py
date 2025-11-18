"""Tests for ArXiv ETL pipeline."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, date
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.pipelines.arxiv_pipeline import ArxivPipeline, ArxivPipelineStats
from app.models.publication import Publication
from app.models.auteur import Auteur
from app.models.theme import Theme


# Mock arXiv paper data
MOCK_PAPER = {
    'id': '2311.12345',
    'title': 'Attention is All You Need',
    'summary': 'We propose the Transformer model.',
    'published': '2023-11-20T00:00:00Z',
    'doi': '10.48550/arXiv.2311.12345',
    'authors': [
        {'name': 'John Smith'},
        {'name': 'Jane Doe'},
    ],
    'categories': ['cs.LG', 'cs.AI'],
}


@pytest.fixture
def pipeline(async_session):
    """Create ArXiv pipeline instance."""
    return ArxivPipeline(async_session, rate_limit_requests=1, rate_limit_period=0.1)


@pytest.mark.asyncio
class TestArxivPipelineStats:
    """Test suite for ArxivPipelineStats."""

    def test_initialization(self):
        """Test stats initialization."""
        stats = ArxivPipelineStats()

        assert stats.papers_collected == 0
        assert stats.papers_created == 0
        assert stats.papers_updated == 0
        assert stats.papers_skipped == 0
        assert stats.authors_created == 0
        assert stats.themes_created == 0
        assert stats.errors == 0

    def test_duration_calculation(self):
        """Test duration calculation."""
        stats = ArxivPipelineStats()
        stats.start_time = datetime(2023, 1, 1, 12, 0, 0)
        stats.end_time = datetime(2023, 1, 1, 12, 5, 30)

        assert stats.duration_seconds == 330.0

    def test_to_dict(self):
        """Test converting stats to dictionary."""
        stats = ArxivPipelineStats()
        stats.papers_collected = 10
        stats.papers_created = 8

        result = stats.to_dict()

        assert result['papers_collected'] == 10
        assert result['papers_created'] == 8
        assert 'duration_seconds' in result


@pytest.mark.asyncio
class TestArxivPipeline:
    """Test suite for ArxivPipeline."""

    async def test_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert pipeline.db is not None
        assert pipeline.collector is not None
        assert pipeline.dedup_service is not None
        assert pipeline.publication_repo is not None

    async def test_context_manager(self, pipeline):
        """Test async context manager."""
        async with pipeline as p:
            assert p.collector._session is not None

        assert pipeline.collector._session is None

    async def test_extract(self, pipeline):
        """Test extract phase."""
        async with pipeline:
            with patch.object(
                pipeline.collector,
                'search',
                return_value=AsyncMock(return_value=[MOCK_PAPER]),
            ) as mock_search:
                mock_search.return_value = [MOCK_PAPER]

                papers = await pipeline.extract("deep learning")

                assert len(papers) == 1
                assert papers[0]['id'] == '2311.12345'
                assert pipeline.stats.papers_collected == 1

    async def test_transform(self, pipeline):
        """Test transform phase."""
        result = await pipeline.transform(MOCK_PAPER)

        assert 'publication' in result
        assert 'authors' in result
        assert 'themes' in result

        assert result['publication']['titre'] == 'Attention is All You Need'
        assert result['publication']['arxiv_id'] == '2311.12345'
        assert len(result['authors']) == 2
        assert 'Machine Learning' in result['themes']

    async def test_transform_extracts_themes_from_text(self, pipeline):
        """Test transform extracts themes from text when no categories."""
        paper = {
            'id': '2311.12345',
            'title': 'Deep Learning for Computer Vision',
            'summary': 'We use neural networks.',
            'published': '2023-11-20T00:00:00Z',
        }

        result = await pipeline.transform(paper)

        assert len(result['themes']) > 0

    async def test_load_creates_new_publication(self, pipeline, async_session):
        """Test load creates new publication."""
        transformed = await pipeline.transform(MOCK_PAPER)

        async with pipeline:
            with patch.object(
                pipeline.dedup_service,
                'find_duplicate',
                return_value=AsyncMock(return_value=None),
            ) as mock_find:
                mock_find.return_value = None

                publication = await pipeline.load(transformed)

                assert publication is not None
                assert publication.titre == 'Attention is All You Need'
                assert pipeline.stats.papers_created == 1

    async def test_load_updates_existing_publication(self, pipeline, async_session):
        """Test load updates existing publication."""
        # Create existing publication
        existing = Publication(
            titre="Attention is All You Need",
            abstract=None,
            doi="10.48550/arXiv.2311.12345",
            date_publication=date.today(),
            type_publication='preprint',
        )
        async_session.add(existing)
        await async_session.commit()

        transformed = await pipeline.transform(MOCK_PAPER)

        async with pipeline:
            with patch.object(
                pipeline.dedup_service,
                'find_duplicate',
                return_value=AsyncMock(return_value=existing),
            ) as mock_find:
                mock_find.return_value = existing

                with patch.object(
                    pipeline.dedup_service,
                    'should_update',
                    return_value=True,
                ):
                    publication = await pipeline.load(transformed)

                    assert pipeline.stats.papers_updated == 1

    async def test_load_skips_duplicate(self, pipeline, async_session):
        """Test load skips duplicate when no update needed."""
        # Create existing publication
        existing = Publication(
            titre="Attention is All You Need",
            abstract="Complete abstract",
            doi="10.48550/arXiv.2311.12345",
            date_publication=date.today(),
            type_publication='preprint',
        )
        async_session.add(existing)
        await async_session.commit()

        transformed = await pipeline.transform(MOCK_PAPER)

        async with pipeline:
            with patch.object(
                pipeline.dedup_service,
                'find_duplicate',
                return_value=AsyncMock(return_value=existing),
            ) as mock_find:
                mock_find.return_value = existing

                with patch.object(
                    pipeline.dedup_service,
                    'should_update',
                    return_value=False,
                ):
                    publication = await pipeline.load(transformed)

                    assert publication is None
                    assert pipeline.stats.papers_skipped == 1

    async def test_find_or_create_author_new(self, pipeline, async_session):
        """Test finding or creating new author."""
        author_data = {
            'nom': 'Smith',
            'prenom': 'John',
            'email': None,
            'h_index': None,
            'homepage_url': None,
        }

        async with pipeline:
            author = await pipeline._find_or_create_author(author_data)

            assert author.nom == 'Smith'
            assert author.prenom == 'John'
            assert pipeline.stats.authors_created == 1

    async def test_find_or_create_author_existing(self, pipeline, async_session):
        """Test finding existing author."""
        # Create existing author
        existing = Auteur(nom='Smith', prenom='John')
        async_session.add(existing)
        await async_session.commit()

        author_data = {
            'nom': 'Smith',
            'prenom': 'John',
            'email': None,
            'h_index': None,
            'homepage_url': None,
        }

        async with pipeline:
            author = await pipeline._find_or_create_author(author_data)

            assert author.id == existing.id
            assert pipeline.stats.authors_created == 0

    async def test_find_or_create_theme_new(self, pipeline, async_session):
        """Test finding or creating new theme."""
        async with pipeline:
            theme = await pipeline._find_or_create_theme('Machine Learning')

            assert theme.label == 'Machine Learning'
            assert pipeline.stats.themes_created == 1

    async def test_find_or_create_theme_existing(self, pipeline, async_session):
        """Test finding existing theme."""
        # Create existing theme
        existing = Theme(label='Machine Learning', niveau_hierarchie=0)
        async_session.add(existing)
        await async_session.commit()

        async with pipeline:
            theme = await pipeline._find_or_create_theme('Machine Learning')

            assert theme.id == existing.id
            assert pipeline.stats.themes_created == 0

    async def test_run_complete_pipeline(self, pipeline, async_session):
        """Test running complete pipeline."""
        async with pipeline:
            with patch.object(
                pipeline.collector,
                'search',
                return_value=AsyncMock(return_value=[MOCK_PAPER]),
            ) as mock_search:
                mock_search.return_value = [MOCK_PAPER]

                stats = await pipeline.run(
                    query="deep learning",
                    categories=['cs.LG'],
                    max_results=10,
                )

                assert stats.papers_collected == 1
                assert stats.papers_created >= 0
                assert stats.start_time is not None
                assert stats.end_time is not None

    async def test_process_paper_handles_errors(self, pipeline, async_session):
        """Test process paper handles errors gracefully."""
        bad_paper = {
            'id': None,  # Invalid paper
            'title': None,
        }

        async with pipeline:
            await pipeline._process_paper(bad_paper)

            assert pipeline.stats.errors == 1

    async def test_handle_authors(self, pipeline, async_session):
        """Test handling authors for publication."""
        publication = Publication(titre="Test", abstract="Abstract", date_publication=date.today(), type_publication='preprint')
        async_session.add(publication)
        await async_session.flush()

        authors_data = [
            {'nom': 'Smith', 'prenom': 'John', 'email': None, 'h_index': None, 'homepage_url': None},
            {'nom': 'Doe', 'prenom': 'Jane', 'email': None, 'h_index': None, 'homepage_url': None},
        ]

        async with pipeline:
            await pipeline._handle_authors(publication, authors_data)

        # Verify relationships were created
        result = await async_session.execute(
            select(Publication)
            .where(Publication.id == publication.id)
            .options(selectinload(Publication.auteurs))
        )
        publication = result.scalar_one()
        assert len(publication.auteurs) == 2

    async def test_handle_themes(self, pipeline, async_session):
        """Test handling themes for publication."""
        publication = Publication(titre="Test", abstract="Abstract", date_publication=date.today(), type_publication='preprint')
        async_session.add(publication)
        await async_session.flush()

        theme_names = ['Machine Learning', 'Computer Vision']

        async with pipeline:
            await pipeline._handle_themes(publication, theme_names)

        # Verify relationships were created
        result = await async_session.execute(
            select(Publication)
            .where(Publication.id == publication.id)
            .options(selectinload(Publication.themes))
        )
        publication = result.scalar_one()
        assert len(publication.themes) == 2
