"""Auteur service with business logic."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.auteur import Auteur
from app.repositories.auteur_repository import AuteurRepository
from app.services.base_service import BaseService


class AuteurService(BaseService[Auteur, AuteurRepository]):
    """
    Service for Auteur entity with business logic.
    
    Provides methods for:
    - Creating authors with affiliations
    - Managing h-index updates
    - Searching by name or ORCID
    - Ranking top contributors
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize AuteurService."""
        repository = AuteurRepository(db)
        super().__init__(repository, db)
    
    async def create_with_affiliations(
        self,
        auteur_data: Dict[str, Any],
        affiliations: Optional[List[Dict[str, Any]]] = None
    ) -> Auteur:
        """
        Create an author and link affiliations.
        
        Args:
            auteur_data: Author data
            affiliations: Optional list of affiliation dictionaries
                Each dict should have: organisation_id, date_debut, date_fin, poste
            
        Returns:
            Created author with linked affiliations
            
        Raises:
            ValueError: If validation fails
        """
        # Create author
        auteur = await self.create(auteur_data)
        
        # TODO: Create affiliations in association table
        # This will be implemented when we have the affiliation repository
        
        return auteur
    
    async def update_h_index(
        self,
        auteur_id: UUID,
        h_index: int
    ) -> Optional[Auteur]:
        """
        Update author's h-index (for Phase 3 Semantic Scholar enrichment).

        Args:
            auteur_id: Author UUID
            h_index: New h-index value

        Returns:
            Updated author if found

        Raises:
            ValueError: If h_index is negative
        """
        if h_index < 0:
            raise ValueError("h-index cannot be negative")

        return await self.update(auteur_id, {"h_index": h_index})
    
    async def get_top_contributors(
        self,
        limit: int = 100,
        min_h_index: int = 10
    ) -> List[Auteur]:
        """
        Get top contributing authors ranked by h-index.

        Args:
            limit: Maximum number of authors to return
            min_h_index: Minimum h-index threshold

        Returns:
            List of top authors
        """
        stmt = (
            select(Auteur)
            .where(Auteur.h_index >= min_h_index)
            .order_by(Auteur.h_index.desc(), Auteur.nombre_citations.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def search_by_name_or_orcid(
        self,
        query: str
    ) -> List[Auteur]:
        """
        Search authors by name or ORCID.
        
        Args:
            query: Search query (name or ORCID)
            
        Returns:
            List of matching authors
        """
        # If query looks like an ORCID (XXXX-XXXX-XXXX-XXXX format)
        if len(query) == 19 and query.count('-') == 3:
            auteur = await self.repository.get_by_orcid(query)
            return [auteur] if auteur else []
        
        # Otherwise search by name
        return await self.repository.search_by_name(query, skip=0, limit=20)
    
    async def get_prolific_authors(
        self,
        min_publications: int = 10,
        limit: int = 100
    ) -> List[Auteur]:
        """
        Get prolific authors with high publication count.

        Args:
            min_publications: Minimum number of publications
            limit: Maximum number of authors to return

        Returns:
            List of prolific authors
        """
        stmt = (
            select(Auteur)
            .where(Auteur.nombre_publications >= min_publications)
            .order_by(Auteur.nombre_publications.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_authors_by_organization(
        self,
        organisation_id: UUID,
        active_only: bool = True
    ) -> List[Auteur]:
        """
        Get all authors affiliated with an organization.

        Args:
            organisation_id: Organization UUID
            active_only: If True, only return currently affiliated authors

        Returns:
            List of authors
        """
        # TODO: Implement once affiliation associations are ready
        # For now, return empty list
        return []
    
    async def _validate_create(self, obj_in: Dict[str, Any]) -> None:
        """
        Validate author data before creation.
        
        Checks:
        - ORCID uniqueness if provided
        - ORCID format validation
        
        Args:
            obj_in: Author data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Validate ORCID format (XXXX-XXXX-XXXX-XXXX)
        if 'orcid' in obj_in and obj_in['orcid']:
            orcid = obj_in['orcid']
            if len(orcid) != 19 or orcid.count('-') != 3:
                raise ValueError(f"Invalid ORCID format: {orcid}. Expected format: XXXX-XXXX-XXXX-XXXX")
            
            # Check uniqueness
            existing = await self.repository.get_by_orcid(orcid)
            if existing:
                raise ValueError(f"Author with ORCID {orcid} already exists")
    
    async def _validate_update(
        self,
        entity_id: UUID,
        obj_in: Dict[str, Any]
    ) -> None:
        """
        Validate author data before update.

        Checks:
        - ORCID uniqueness if being updated (excluding current author)
        - ORCID format validation
        - h-index validity

        Args:
            entity_id: Author UUID being updated
            obj_in: Author data to validate

        Raises:
            ValueError: If validation fails
        """
        # Validate ORCID if provided
        if 'orcid' in obj_in and obj_in['orcid']:
            orcid = obj_in['orcid']

            # Format validation
            if len(orcid) != 19 or orcid.count('-') != 3:
                raise ValueError(f"Invalid ORCID format: {orcid}. Expected format: XXXX-XXXX-XXXX-XXXX")

            # Uniqueness check
            existing = await self.repository.get_by_orcid(orcid)
            if existing and existing.id != entity_id:
                raise ValueError(f"Author with ORCID {orcid} already exists")

        # Validate h-index if provided
        if 'h_index' in obj_in and obj_in['h_index'] is not None:
            if obj_in['h_index'] < 0:
                raise ValueError("h-index cannot be negative")
