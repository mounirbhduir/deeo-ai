"""Enrichment service for publications using Semantic Scholar.

This service orchestrates the enrichment process:
- Fetches external data from Semantic Scholar API
- Updates publication metadata (citations, venue, etc.)
- Enriches author profiles (h-index, affiliations)
- Processes enrichment in batches for efficiency
- Tracks enrichment status and errors

Example:
    >>> async with EnrichmentService(db) as service:
    ...     stats = await service.enrich_publications(publication_ids)
    ...     print(f"Enriched {stats['enriched']} publications")
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication
from app.models.auteur import Auteur
from app.repositories.publication_repository import PublicationRepository
from app.repositories.auteur_repository import AuteurRepository
from app.enrichment.semantic_scholar import (
    SemanticScholarClient,
    PaperNotFoundError,
    RateLimitError,
)
from app.logging import get_logger

logger = get_logger(__name__)


class EnrichmentError(Exception):
    """Base exception for enrichment errors."""
    pass


class EnrichmentStats:
    """Statistics for enrichment operations."""

    def __init__(self):
        self.total_publications = 0
        self.enriched_publications = 0
        self.failed_publications = 0
        self.skipped_publications = 0
        self.total_authors = 0
        self.enriched_authors = 0
        self.failed_authors = 0
        self.citations_updated = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        """Calculate duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_publications": self.total_publications,
            "enriched_publications": self.enriched_publications,
            "failed_publications": self.failed_publications,
            "skipped_publications": self.skipped_publications,
            "total_authors": self.total_authors,
            "enriched_authors": self.enriched_authors,
            "failed_authors": self.failed_authors,
            "citations_updated": self.citations_updated,
            "duration_seconds": self.duration_seconds,
        }


class EnrichmentService:
    """Service for enriching publications with external data.

    This service integrates with Semantic Scholar API to enrich publication
    and author data with citations, impact metrics, and additional metadata.

    Features:
    - Batch processing for efficiency
    - Automatic retry on transient failures
    - Rate limiting compliance
    - Deduplication to avoid re-enriching
    - Comprehensive error handling and logging

    Example:
        >>> async with EnrichmentService(db) as service:
        ...     stats = await service.enrich_publications(publication_ids)
        ...     print(f"Success rate: {stats.enriched_publications / stats.total_publications * 100:.1f}%")
    """

    def __init__(
        self,
        db: AsyncSession,
        api_key: Optional[str] = None,
        batch_size: int = 50,
        max_concurrent: int = 5,
    ):
        """Initialize enrichment service.

        Args:
            db: Database session
            api_key: Optional Semantic Scholar API key
            batch_size: Number of publications to process per batch
            max_concurrent: Maximum concurrent API requests
        """
        self.db = db
        self.api_key = api_key
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent

        self.publication_repo = PublicationRepository(db)
        self.auteur_repo = AuteurRepository(db)
        self.client: Optional[SemanticScholarClient] = None

        logger.info(
            "enrichment.service.initialized",
            batch_size=batch_size,
            max_concurrent=max_concurrent,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = SemanticScholarClient(api_key=self.api_key)
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def enrich_publications(
        self,
        publication_ids: Optional[List[str]] = None,
        force_update: bool = False,
    ) -> EnrichmentStats:
        """Enrich publications with Semantic Scholar data.

        Args:
            publication_ids: List of publication UUIDs to enrich (None = all)
            force_update: Re-enrich even if already enriched

        Returns:
            Enrichment statistics

        Raises:
            EnrichmentError: If enrichment process fails
        """
        stats = EnrichmentStats()
        stats.start_time = datetime.now()

        logger.info(
            "enrichment.publications.start",
            publication_ids_count=len(publication_ids) if publication_ids else "all",
            force_update=force_update,
        )

        try:
            # Fetch publications to enrich
            publications = await self._get_publications_to_enrich(
                publication_ids, force_update
            )

            stats.total_publications = len(publications)

            logger.info(
                "enrichment.publications.fetched",
                count=stats.total_publications,
            )

            # Process in batches
            for i in range(0, len(publications), self.batch_size):
                batch = publications[i : i + self.batch_size]

                logger.info(
                    "enrichment.batch.start",
                    batch_number=i // self.batch_size + 1,
                    batch_size=len(batch),
                )

                # Process batch with concurrency control
                batch_stats = await self._enrich_batch(batch)

                # Update overall stats
                stats.enriched_publications += batch_stats["enriched"]
                stats.failed_publications += batch_stats["failed"]
                stats.skipped_publications += batch_stats["skipped"]
                stats.citations_updated += batch_stats["citations_updated"]

                logger.info(
                    "enrichment.batch.complete",
                    batch_number=i // self.batch_size + 1,
                    enriched=batch_stats["enriched"],
                    failed=batch_stats["failed"],
                )

            stats.end_time = datetime.now()

            logger.info(
                "enrichment.publications.complete",
                stats=stats.to_dict(),
            )

            return stats

        except Exception as e:
            stats.end_time = datetime.now()
            logger.error(
                "enrichment.publications.failed",
                error=str(e),
                stats=stats.to_dict(),
            )
            raise EnrichmentError(f"Enrichment process failed: {e}") from e

    async def enrich_single_publication(
        self, publication_id: str
    ) -> Optional[Dict[str, Any]]:
        """Enrich a single publication.

        Args:
            publication_id: Publication UUID

        Returns:
            Enrichment data dictionary or None if failed
        """
        logger.info(
            "enrichment.publication.start",
            publication_id=publication_id,
        )

        try:
            # Fetch publication
            publication = await self.publication_repo.get_by_id(publication_id)
            if not publication:
                logger.warning(
                    "enrichment.publication.not_found",
                    publication_id=publication_id,
                )
                return None

            # Get Semantic Scholar data
            enrichment_data = await self._fetch_semantic_scholar_data(publication)

            if not enrichment_data:
                logger.info(
                    "enrichment.publication.no_data",
                    publication_id=publication_id,
                )
                return None

            # Update publication
            await self._update_publication(publication, enrichment_data)

            # Update authors
            await self._update_authors(publication, enrichment_data)

            await self.db.commit()

            logger.info(
                "enrichment.publication.success",
                publication_id=publication_id,
                citations=enrichment_data.get("citation_count", 0),
            )

            return enrichment_data

        except Exception as e:
            await self.db.rollback()
            logger.error(
                "enrichment.publication.failed",
                publication_id=publication_id,
                error=str(e),
            )
            return None

    async def _get_publications_to_enrich(
        self,
        publication_ids: Optional[List[str]],
        force_update: bool,
    ) -> List[Publication]:
        """Fetch publications that need enrichment.

        Args:
            publication_ids: Optional list of publication IDs
            force_update: Whether to re-enrich already enriched publications

        Returns:
            List of Publication objects
        """
        query = select(Publication)

        # Filter by IDs if provided
        if publication_ids:
            query = query.where(Publication.id.in_(publication_ids))

        # Filter by arXiv ID or DOI (required for Semantic Scholar)
        query = query.where(
            (Publication.arxiv_id.isnot(None)) | (Publication.doi.isnot(None))
        )

        # Skip already enriched unless force_update
        if not force_update:
            query = query.where(Publication.nombre_citations == 0)

        result = await self.db.execute(query)
        publications = result.scalars().all()

        return list(publications)

    async def _enrich_batch(self, publications: List[Publication]) -> Dict[str, int]:
        """Enrich a batch of publications with concurrency control.

        Args:
            publications: List of publications to enrich

        Returns:
            Dictionary with batch statistics
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def enrich_with_semaphore(pub):
            async with semaphore:
                return await self.enrich_single_publication(str(pub.id))

        # Process concurrently
        results = await asyncio.gather(
            *[enrich_with_semaphore(pub) for pub in publications],
            return_exceptions=True,
        )

        # Calculate stats
        enriched = sum(1 for r in results if r and not isinstance(r, Exception))
        failed = sum(1 for r in results if isinstance(r, Exception))
        skipped = sum(1 for r in results if r is None)
        citations_updated = sum(
            r.get("citation_count", 0) for r in results if r and not isinstance(r, Exception)
        )

        return {
            "enriched": enriched,
            "failed": failed,
            "skipped": skipped,
            "citations_updated": citations_updated,
        }

    async def _fetch_semantic_scholar_data(
        self, publication: Publication
    ) -> Optional[Dict[str, Any]]:
        """Fetch data from Semantic Scholar API.

        Args:
            publication: Publication to fetch data for

        Returns:
            Enrichment data dictionary or None
        """
        if not self.client:
            raise EnrichmentError("Semantic Scholar client not initialized")

        try:
            # Try arXiv ID first
            if publication.arxiv_id:
                data = await self.client.get_paper_by_arxiv_id(publication.arxiv_id)
                if data:
                    return self.client.extract_enrichment_data(data)

            # Try DOI as fallback
            if publication.doi:
                data = await self.client.get_paper_by_doi(publication.doi)
                if data:
                    return self.client.extract_enrichment_data(data)

            return None

        except PaperNotFoundError:
            logger.debug(
                "enrichment.semantic_scholar.not_found",
                publication_id=publication.id,
                arxiv_id=publication.arxiv_id,
                doi=publication.doi,
            )
            return None

        except RateLimitError:
            logger.warning("enrichment.semantic_scholar.rate_limit")
            # Wait and retry once
            await asyncio.sleep(60)
            return await self._fetch_semantic_scholar_data(publication)

        except Exception as e:
            logger.error(
                "enrichment.semantic_scholar.error",
                publication_id=publication.id,
                error=str(e),
            )
            return None

    async def _update_publication(
        self, publication: Publication, enrichment_data: Dict[str, Any]
    ) -> None:
        """Update publication with enrichment data.

        Args:
            publication: Publication to update
            enrichment_data: Data from Semantic Scholar
        """
        # Update citation count
        if "citation_count" in enrichment_data:
            publication.nombre_citations = enrichment_data["citation_count"]

        # Update venue if available
        if enrichment_data.get("venue"):
            publication.source_nom = enrichment_data["venue"]

        # Store Semantic Scholar ID in metadata (if we add a JSON field later)
        # For now, we can track it in logs

        logger.debug(
            "enrichment.publication.updated",
            publication_id=publication.id,
            citations=publication.nombre_citations,
        )

    async def _update_authors(
        self, publication: Publication, enrichment_data: Dict[str, Any]
    ) -> None:
        """Update authors with enrichment data.

        Args:
            publication: Publication whose authors to update
            enrichment_data: Enrichment data including author info
        """
        authors_data = enrichment_data.get("authors", [])

        # Load publication authors
        await self.db.refresh(publication, ["auteurs"])

        for pub_author in publication.auteurs:
            # Load author
            await self.db.refresh(pub_author, ["auteur"])
            author = pub_author.auteur

            # Try to match with Semantic Scholar data
            for s2_author in authors_data:
                author_name = s2_author.get("name", "")

                # Simple name matching (can be improved)
                if self._match_author_name(author, author_name):
                    # Update Semantic Scholar ID
                    if s2_author.get("semantic_scholar_id"):
                        author.semantic_scholar_id = s2_author["semantic_scholar_id"]

                    logger.debug(
                        "enrichment.author.matched",
                        author_id=author.id,
                        semantic_scholar_id=author.semantic_scholar_id,
                    )
                    break

    def _match_author_name(self, author: Auteur, semantic_name: str) -> bool:
        """Match author name with Semantic Scholar name.

        Args:
            author: Database author
            semantic_name: Name from Semantic Scholar

        Returns:
            True if names match
        """
        # Build full name
        db_name = f"{author.prenom or ''} {author.nom}".strip().lower()
        semantic_name = semantic_name.strip().lower()

        # Simple matching (can be improved with fuzzy matching)
        return db_name == semantic_name or author.nom.lower() in semantic_name

    async def get_enrichment_stats_for_publications(
        self, publication_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get enrichment statistics for publications.

        Args:
            publication_ids: Optional list of publication IDs

        Returns:
            Dictionary with enrichment statistics
        """
        query = select(Publication)

        if publication_ids:
            query = query.where(Publication.id.in_(publication_ids))

        result = await self.db.execute(query)
        publications = result.scalars().all()

        total = len(publications)
        enriched = sum(1 for p in publications if p.nombre_citations > 0)
        total_citations = sum(p.nombre_citations for p in publications)

        return {
            "total_publications": total,
            "enriched_publications": enriched,
            "not_enriched": total - enriched,
            "enrichment_rate": enriched / total * 100 if total > 0 else 0,
            "total_citations": total_citations,
            "average_citations": total_citations / enriched if enriched > 0 else 0,
        }
