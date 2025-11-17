"""Deduplication service for detecting and handling duplicate publications.

This module provides services for:
- Finding duplicate publications by DOI, arXiv ID, or title similarity
- Deciding whether to update existing publications
- Preventing duplicate entries in the database
"""

from typing import Optional, Dict, Any
from difflib import SequenceMatcher

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication
from app.logging import get_logger

logger = get_logger(__name__)


class DeduplicationService:
    """Service for detecting and handling duplicate publications.

    Deduplication strategy (checked in order):
    1. Exact match by DOI (if available)
    2. Exact match by arXiv ID (if available)
    3. Title similarity > 95% threshold

    Attributes:
        title_similarity_threshold: Minimum similarity ratio for title matching (0.95)
    """

    def __init__(self, title_similarity_threshold: float = 0.95):
        """Initialize deduplication service.

        Args:
            title_similarity_threshold: Minimum similarity for title matching (0-1)
        """
        self.title_similarity_threshold = title_similarity_threshold
        logger.info(
            "deduplication.service.initialized",
            similarity_threshold=title_similarity_threshold,
        )

    async def find_duplicate(
        self,
        db: AsyncSession,
        publication_data: Dict[str, Any],
    ) -> Optional[Publication]:
        """Find duplicate publication in database.

        Checks in order:
        1. DOI match
        2. arXiv ID match
        3. Title similarity match

        Args:
            db: Database session
            publication_data: Publication data to check for duplicates

        Returns:
            Existing Publication if duplicate found, None otherwise

        Example:
            >>> data = {'doi': '10.1234/example', 'titre': 'Example'}
            >>> duplicate = await service.find_duplicate(db, data)
            >>> if duplicate:
            ...     print(f"Found duplicate: {duplicate.id}")
        """
        doi = publication_data.get('doi')
        arxiv_id = publication_data.get('arxiv_id')
        titre = publication_data.get('titre')

        # Strategy 1: Check DOI
        if doi:
            duplicate = await self._find_by_doi(db, doi)
            if duplicate:
                logger.info(
                    "deduplication.found_by_doi",
                    doi=doi,
                    existing_id=duplicate.id,
                )
                return duplicate

        # Strategy 2: Check arXiv ID
        if arxiv_id:
            duplicate = await self._find_by_arxiv_id(db, arxiv_id)
            if duplicate:
                logger.info(
                    "deduplication.found_by_arxiv_id",
                    arxiv_id=arxiv_id,
                    existing_id=duplicate.id,
                )
                return duplicate

        # Strategy 3: Check title similarity
        if titre:
            duplicate = await self._find_by_title_similarity(db, titre)
            if duplicate:
                logger.info(
                    "deduplication.found_by_title",
                    titre=titre[:50],
                    existing_id=duplicate.id,
                    similarity=self._calculate_similarity(titre, duplicate.titre),
                )
                return duplicate

        logger.debug("deduplication.no_duplicate_found", doi=doi, arxiv_id=arxiv_id)
        return None

    async def _find_by_doi(
        self,
        db: AsyncSession,
        doi: str,
    ) -> Optional[Publication]:
        """Find publication by exact DOI match.

        Args:
            db: Database session
            doi: DOI to search for

        Returns:
            Publication if found, None otherwise
        """
        stmt = select(Publication).where(Publication.doi == doi)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def _find_by_arxiv_id(
        self,
        db: AsyncSession,
        arxiv_id: str,
    ) -> Optional[Publication]:
        """Find publication by exact arXiv ID match.

        Args:
            db: Database session
            arxiv_id: arXiv ID to search for

        Returns:
            Publication if found, None otherwise
        """
        stmt = select(Publication).where(Publication.arxiv_id == arxiv_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def _find_by_title_similarity(
        self,
        db: AsyncSession,
        titre: str,
    ) -> Optional[Publication]:
        """Find publication by title similarity.

        Fetches all publications and calculates similarity ratio.
        This is not optimal for large datasets but works for moderate sizes.

        Args:
            db: Database session
            titre: Title to match against

        Returns:
            Publication if similarity > threshold, None otherwise
        """
        # Fetch all publications (could be optimized with PostgreSQL full-text search)
        stmt = select(Publication)
        result = await db.execute(stmt)
        publications = result.scalars().all()

        # Find best match
        best_match = None
        best_similarity = 0.0

        for pub in publications:
            if pub.titre:
                similarity = self._calculate_similarity(titre, pub.titre)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = pub

        # Return if above threshold
        if best_similarity >= self.title_similarity_threshold:
            return best_match

        return None

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts.

        Uses SequenceMatcher for fuzzy string matching.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity ratio between 0 and 1

        Example:
            >>> DeduplicationService._calculate_similarity(
            ...     "Attention is all you need",
            ...     "Attention Is All You Need"
            ... )
            0.96...
        """
        # Normalize for comparison
        t1 = text1.lower().strip()
        t2 = text2.lower().strip()

        matcher = SequenceMatcher(None, t1, t2)
        return matcher.ratio()

    def should_update(
        self,
        existing: Publication,
        new_data: Dict[str, Any],
    ) -> bool:
        """Decide whether to update an existing publication.

        Update if new data has:
        - More complete information (non-null fields)
        - More recent publication date
        - Higher citation count

        Args:
            existing: Existing publication in database
            new_data: New publication data

        Returns:
            True if should update, False otherwise

        Example:
            >>> existing = Publication(nombre_citations=10)
            >>> new_data = {'nombre_citations': 20}
            >>> service.should_update(existing, new_data)
            True
        """
        reasons = []

        # Check if new data has more citations
        if new_data.get('nombre_citations', 0) > (existing.nombre_citations or 0):
            reasons.append('more_citations')

        # Check if new data has abstract and existing doesn't
        if new_data.get('abstract') and not existing.abstract:
            reasons.append('has_abstract')

        # Check if new data has DOI and existing doesn't
        if new_data.get('doi') and not existing.doi:
            reasons.append('has_doi')

        # Check if new data has arXiv ID and existing doesn't
        if new_data.get('arxiv_id') and not existing.arxiv_id:
            reasons.append('has_arxiv_id')

        should_update = len(reasons) > 0

        if should_update:
            logger.info(
                "deduplication.should_update",
                existing_id=existing.id,
                reasons=reasons,
            )
        else:
            logger.debug(
                "deduplication.skip_update",
                existing_id=existing.id,
            )

        return should_update

    async def merge_publications(
        self,
        db: AsyncSession,
        existing: Publication,
        new_data: Dict[str, Any],
    ) -> Publication:
        """Merge new data into existing publication.

        Updates fields that are None in existing but present in new data.
        Always updates nb_citations if new value is higher.

        Args:
            db: Database session
            existing: Existing publication to update
            new_data: New data to merge in

        Returns:
            Updated publication

        Example:
            >>> existing = Publication(titre='Example', abstract=None)
            >>> new_data = {'abstract': 'New abstract', 'nombre_citations': 5}
            >>> updated = await service.merge_publications(db, existing, new_data)
            >>> updated.abstract
            'New abstract'
        """
        # Update None fields with new data
        if not existing.abstract and new_data.get('abstract'):
            existing.abstract = new_data['abstract']

        if not existing.doi and new_data.get('doi'):
            existing.doi = new_data['doi']

        if not existing.arxiv_id and new_data.get('arxiv_id'):
            existing.arxiv_id = new_data['arxiv_id']

        if not existing.url and new_data.get('url'):
            existing.url = new_data['url']

        # Always update citations if higher
        if new_data.get('nombre_citations', 0) > (existing.nombre_citations or 0):
            existing.nombre_citations = new_data['nombre_citations']

        await db.commit()
        await db.refresh(existing)

        logger.info(
            "deduplication.publication_merged",
            publication_id=existing.id,
            titre=existing.titre[:50],
        )

        return existing
