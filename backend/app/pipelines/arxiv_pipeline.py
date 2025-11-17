"""Complete ETL pipeline for arXiv data collection and processing.

This module orchestrates the full ETL process:
- Extract: Collect papers from arXiv API
- Transform: Map arXiv data to database models
- Load: Save to PostgreSQL with deduplication
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication
from app.models.auteur import Auteur
from app.models.theme import Theme
from app.models.publication_auteur import PublicationAuteur
from app.models.publication_theme import PublicationTheme
from app.repositories.publication_repository import PublicationRepository
from app.repositories.auteur_repository import AuteurRepository
from app.repositories.theme_repository import ThemeRepository
from app.pipelines.arxiv_collector import ArxivCollector
from app.pipelines.arxiv_mappers import (
    ArxivToPublicationMapper,
    ArxivToAuteurMapper,
    ArxivCategoryMapper,
)
from app.pipelines.deduplication import DeduplicationService
from app.logging import get_logger

logger = get_logger(__name__)


class ArxivPipelineError(Exception):
    """Base exception for ArXiv pipeline errors."""
    pass


class ArxivPipelineStats:
    """Statistics for pipeline execution."""

    def __init__(self):
        self.papers_collected = 0
        self.papers_created = 0
        self.papers_updated = 0
        self.papers_skipped = 0
        self.authors_created = 0
        self.themes_created = 0
        self.errors = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        """Calculate pipeline duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'papers_collected': self.papers_collected,
            'papers_created': self.papers_created,
            'papers_updated': self.papers_updated,
            'papers_skipped': self.papers_skipped,
            'authors_created': self.authors_created,
            'themes_created': self.themes_created,
            'errors': self.errors,
            'duration_seconds': self.duration_seconds,
        }


class ArxivPipeline:
    """Complete ETL pipeline for arXiv data collection.

    Features:
    - Asynchronous data collection with rate limiting
    - Automatic data transformation and mapping
    - Deduplication to prevent duplicates
    - Author and theme relationship management
    - Comprehensive error handling and logging
    - Detailed execution statistics

    Example:
        >>> async with ArxivPipeline(db) as pipeline:
        ...     stats = await pipeline.run(
        ...         query="deep learning",
        ...         categories=["cs.LG"],
        ...         max_results=100
        ...     )
        ...     print(f"Created {stats.papers_created} papers")
    """

    def __init__(
        self,
        db: AsyncSession,
        rate_limit_requests: int = 1,
        rate_limit_period: float = 3.0,
    ):
        """Initialize ArXiv pipeline.

        Args:
            db: Database session
            rate_limit_requests: Requests per period for rate limiting
            rate_limit_period: Time period in seconds for rate limiting
        """
        self.db = db
        self.collector = ArxivCollector(rate_limit_requests, rate_limit_period)
        self.dedup_service = DeduplicationService()
        self.publication_repo = PublicationRepository(db)
        self.auteur_repo = AuteurRepository(db)
        self.theme_repo = ThemeRepository(db)
        self.stats = ArxivPipelineStats()

        logger.info("arxiv.pipeline.initialized")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.collector.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.collector.__aexit__(exc_type, exc_val, exc_tb)

    async def run(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        date_range: Optional[tuple[datetime, datetime]] = None,
        max_results: int = 100,
    ) -> ArxivPipelineStats:
        """Run complete ETL pipeline.

        Args:
            query: Search query string
            categories: List of arXiv categories to filter
            date_range: Date range for filtering results
            max_results: Maximum number of papers to collect

        Returns:
            Pipeline execution statistics

        Raises:
            ArxivPipelineError: If pipeline execution fails
        """
        self.stats = ArxivPipelineStats()
        self.stats.start_time = datetime.now()

        logger.info(
            "arxiv.pipeline.start",
            query=query,
            categories=categories,
            max_results=max_results,
        )

        try:
            # Extract: Collect papers from arXiv
            papers = await self.extract(query, categories, date_range, max_results)

            # Transform & Load: Process each paper
            for paper in papers:
                await self._process_paper(paper)

            self.stats.end_time = datetime.now()

            logger.info(
                "arxiv.pipeline.complete",
                stats=self.stats.to_dict(),
            )

            return self.stats

        except Exception as e:
            self.stats.end_time = datetime.now()
            logger.error(
                "arxiv.pipeline.failed",
                error=str(e),
                stats=self.stats.to_dict(),
            )
            raise ArxivPipelineError(f"Pipeline execution failed: {e}") from e

    async def extract(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        date_range: Optional[tuple[datetime, datetime]] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """Extract papers from arXiv API.

        Args:
            query: Search query string
            categories: List of arXiv categories
            date_range: Date range for filtering
            max_results: Maximum results to fetch

        Returns:
            List of paper dictionaries from arXiv
        """
        logger.info("arxiv.pipeline.extract.start", query=query)

        papers = await self.collector.search(
            query=query,
            categories=categories,
            date_range=date_range,
            max_results=max_results,
        )

        self.stats.papers_collected = len(papers)

        logger.info(
            "arxiv.pipeline.extract.complete",
            count=len(papers),
        )

        return papers

    async def transform(self, arxiv_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Transform arXiv paper to database format.

        Args:
            arxiv_paper: Paper data from arXiv API

        Returns:
            Transformed data ready for database insertion
        """
        # Map publication data
        publication_data = ArxivToPublicationMapper.map(arxiv_paper)

        # Map authors
        authors_data = []
        if arxiv_paper.get('authors'):
            authors_data = ArxivToAuteurMapper.map_authors(arxiv_paper['authors'])

        # Map categories to themes
        themes = []
        if arxiv_paper.get('categories'):
            themes = ArxivCategoryMapper.map_categories(arxiv_paper['categories'])

        # Extract themes from title/abstract if no categories
        if not themes and publication_data.get('titre'):
            text = f"{publication_data['titre']} {publication_data.get('abstract', '')}"
            themes = ArxivCategoryMapper.extract_themes_from_text(text)

        return {
            'publication': publication_data,
            'authors': authors_data,
            'themes': themes,
        }

    async def load(self, transformed_data: Dict[str, Any]) -> Optional[Publication]:
        """Load transformed data into database.

        Handles:
        - Deduplication
        - Publication creation/update
        - Author relationships
        - Theme relationships

        Args:
            transformed_data: Transformed data from transform()

        Returns:
            Created or updated Publication, or None if skipped
        """
        publication_data = transformed_data['publication']

        # Check for duplicates
        existing = await self.dedup_service.find_duplicate(self.db, publication_data)

        if existing:
            # Update if needed
            if self.dedup_service.should_update(existing, publication_data):
                publication = await self.dedup_service.merge_publications(
                    self.db,
                    existing,
                    publication_data,
                )
                self.stats.papers_updated += 1
                logger.info(
                    "arxiv.pipeline.load.updated",
                    publication_id=publication.id,
                )
            else:
                self.stats.papers_skipped += 1
                logger.debug(
                    "arxiv.pipeline.load.skipped",
                    publication_id=existing.id,
                )
                return None
        else:
            # Create new publication
            publication = Publication(**publication_data)
            self.db.add(publication)
            await self.db.flush()
            self.stats.papers_created += 1

            logger.info(
                "arxiv.pipeline.load.created",
                publication_id=publication.id,
                titre=publication.titre[:50],
            )

        # Handle authors
        await self._handle_authors(publication, transformed_data['authors'])

        # Handle themes
        await self._handle_themes(publication, transformed_data['themes'])

        await self.db.commit()
        await self.db.refresh(publication)

        return publication

    async def _process_paper(self, arxiv_paper: Dict[str, Any]) -> None:
        """Process a single paper through transform and load stages.

        Args:
            arxiv_paper: Paper data from arXiv API
        """
        try:
            # Transform
            transformed = await self.transform(arxiv_paper)

            # Load
            await self.load(transformed)

        except Exception as e:
            self.stats.errors += 1
            logger.error(
                "arxiv.pipeline.process_paper.failed",
                arxiv_id=arxiv_paper.get('id'),
                error=str(e),
            )

    async def _handle_authors(
        self,
        publication: Publication,
        authors_data: List[Dict[str, Any]],
    ) -> None:
        """Handle author relationships for a publication.

        Creates authors if they don't exist and links them to publication.

        Args:
            publication: Publication to link authors to
            authors_data: List of author dictionaries
        """
        for idx, author_data in enumerate(authors_data):
            # Find or create author
            author = await self._find_or_create_author(author_data)

            # Create publication-author relationship
            pub_author = PublicationAuteur(
                publication_id=publication.id,
                auteur_id=author.id,
                ordre=idx + 1,
            )
            self.db.add(pub_author)

        logger.debug(
            "arxiv.pipeline.authors.handled",
            publication_id=publication.id,
            count=len(authors_data),
        )

    async def _find_or_create_author(self, author_data: Dict[str, Any]) -> Auteur:
        """Find existing author or create new one.

        Args:
            author_data: Author dictionary

        Returns:
            Auteur instance
        """
        # Try to find by name
        nom = author_data.get('nom')
        prenom = author_data.get('prenom')

        if nom:
            existing = await self.auteur_repo.get_by_name(nom, prenom)
            if existing:
                return existing

        # Create new author
        author = Auteur(**author_data)
        self.db.add(author)
        await self.db.flush()
        self.stats.authors_created += 1

        logger.debug(
            "arxiv.pipeline.author.created",
            author_id=author.id,
            nom=nom,
            prenom=prenom,
        )

        return author

    async def _handle_themes(
        self,
        publication: Publication,
        theme_names: List[str],
    ) -> None:
        """Handle theme relationships for a publication.

        Creates themes if they don't exist and links them to publication.

        Args:
            publication: Publication to link themes to
            theme_names: List of theme names
        """
        for theme_name in theme_names:
            # Find or create theme
            theme = await self._find_or_create_theme(theme_name)

            # Create publication-theme relationship
            pub_theme = PublicationTheme(
                publication_id=publication.id,
                theme_id=theme.id,
            )
            self.db.add(pub_theme)

        logger.debug(
            "arxiv.pipeline.themes.handled",
            publication_id=publication.id,
            count=len(theme_names),
        )

    async def _find_or_create_theme(self, theme_name: str) -> Theme:
        """Find existing theme or create new one.

        Args:
            theme_name: Theme name

        Returns:
            Theme instance
        """
        # Try to find by label
        existing = await self.theme_repo.get_by_nom(theme_name)
        if existing:
            return existing

        # Create new theme
        theme = Theme(label=theme_name, description=None, niveau_hierarchie=0)
        self.db.add(theme)
        await self.db.flush()
        self.stats.themes_created += 1

        logger.debug(
            "arxiv.pipeline.theme.created",
            theme_id=theme.id,
            label=theme_name,
        )

        return theme
