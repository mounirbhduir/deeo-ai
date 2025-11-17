"""Publication service with business logic."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.publication import Publication
from app.repositories.publication_repository import PublicationRepository
from app.services.base_service import BaseService


class PublicationService(BaseService[Publication, PublicationRepository]):
    """
    Service for Publication entity with business logic.
    
    Provides methods for:
    - Creating publications with authors
    - Managing enrichment status
    - Full-text search
    - Citation ranking
    - Theme-based filtering
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize PublicationService."""
        repository = PublicationRepository(db)
        super().__init__(repository, db)
    
    async def create_with_authors(
        self,
        pub_data: Dict[str, Any],
        author_ids: List[UUID],
        ordre: Optional[List[int]] = None
    ) -> Publication:
        """
        Create a publication and link it with authors.

        Args:
            pub_data: Publication data
            author_ids: List of author UUIDs to link
            ordre: Optional list of author positions (1-based)

        Returns:
            Created publication with linked authors

        Raises:
            ValueError: If validation fails or authors not found
        """
        # Validate author IDs
        if not author_ids:
            raise ValueError("At least one author is required")

        # Create publication
        publication = await self.create(pub_data)

        # Link authors
        if ordre is None:
            ordre = list(range(1, len(author_ids) + 1))

        if len(ordre) != len(author_ids):
            raise ValueError("ordre list must match author_ids length")

        # TODO: Create associations in association table
        # This will be implemented when we have the association repository

        return publication
    
    async def update_status(
        self,
        publication_id: UUID,
        status: str
    ) -> Optional[Publication]:
        """
        Update publication enrichment status (for Phase 3 pipeline).

        Args:
            publication_id: Publication UUID
            status: New status ('pending_enrichment', 'enriched', 'enrichment_failed')

        Returns:
            Updated publication if found

        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = ['pending_enrichment', 'enriched', 'enrichment_failed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        return await self.update(publication_id, {"status": status})
    
    async def get_pending_enrichment(self, limit: int = 100) -> List[Publication]:
        """
        Get publications pending enrichment (for Phase 3 pipeline).
        
        Args:
            limit: Maximum number of publications to return
            
        Returns:
            List of publications with status 'pending_enrichment'
        """
        return await self.repository.get_by_status('pending_enrichment', skip=0, limit=limit)
    
    async def search_full_text(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Publication]:
        """
        Search publications using full-text search on title and abstract.
        
        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching publications ranked by relevance
        """
        return await self.repository.search(query, skip=skip, limit=limit)
    
    async def get_recent_by_theme(
        self,
        theme_id: UUID,
        days: int = 30,
        limit: int = 20
    ) -> List[Publication]:
        """
        Get recent publications for a specific theme.

        Args:
            theme_id: Theme UUID
            days: Number of days to look back
            limit: Maximum number of publications to return

        Returns:
            List of recent publications for the theme
        """
        # TODO: This requires joining with publication_theme table
        # For now, return publications by date only
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = (
            select(Publication)
            .where(Publication.date_publication >= cutoff_date)
            .order_by(Publication.date_publication.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_top_cited(
        self,
        limit: int = 100,
        min_citations: int = 10
    ) -> List[Publication]:
        """
        Get most cited publications.
        
        Args:
            limit: Maximum number of publications to return
            min_citations: Minimum citation count threshold
            
        Returns:
            List of top cited publications
        """
        stmt = (
            select(Publication)
            .where(Publication.nombre_citations >= min_citations)
            .order_by(Publication.nombre_citations.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def _validate_create(self, obj_in: Dict[str, Any]) -> None:
        """
        Validate publication data before creation.
        
        Checks:
        - DOI uniqueness if provided
        - arXiv ID uniqueness if provided
        
        Args:
            obj_in: Publication data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check DOI uniqueness
        if 'doi' in obj_in and obj_in['doi']:
            existing = await self.repository.get_by_doi(obj_in['doi'])
            if existing:
                raise ValueError(f"Publication with DOI {obj_in['doi']} already exists")
        
        # Check arXiv ID uniqueness
        if 'arxiv_id' in obj_in and obj_in['arxiv_id']:
            existing = await self.repository.get_by_arxiv_id(obj_in['arxiv_id'])
            if existing:
                raise ValueError(f"Publication with arXiv ID {obj_in['arxiv_id']} already exists")
    
    async def _validate_update(
        self,
        entity_id: UUID,
        obj_in: Dict[str, Any]
    ) -> None:
        """
        Validate publication data before update.

        Checks:
        - DOI uniqueness if being updated (excluding current publication)
        - arXiv ID uniqueness if being updated (excluding current publication)
        - Status validity if being updated

        Args:
            entity_id: Publication UUID being updated
            obj_in: Publication data to validate

        Raises:
            ValueError: If validation fails
        """
        # Check DOI uniqueness (if changing)
        if 'doi' in obj_in and obj_in['doi']:
            existing = await self.repository.get_by_doi(obj_in['doi'])
            if existing and existing.id != entity_id:
                raise ValueError(f"Publication with DOI {obj_in['doi']} already exists")

        # Check arXiv ID uniqueness (if changing)
        if 'arxiv_id' in obj_in and obj_in['arxiv_id']:
            existing = await self.repository.get_by_arxiv_id(obj_in['arxiv_id'])
            if existing and existing.id != entity_id:
                raise ValueError(f"Publication with arXiv ID {obj_in['arxiv_id']} already exists")

        # Validate status if provided
        if 'status' in obj_in:
            valid_statuses = ['pending_enrichment', 'enriched', 'enrichment_failed']
            if obj_in['status'] not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
