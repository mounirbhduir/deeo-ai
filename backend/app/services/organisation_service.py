"""Organisation service with business logic."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.organisation import Organisation
from app.repositories.organisation_repository import OrganisationRepository
from app.services.base_service import BaseService


class OrganisationService(BaseService[Organisation, OrganisationRepository]):
    """
    Service for Organisation entity with business logic.
    
    Provides methods for:
    - Searching organizations
    - Filtering by country
    - Managing organization metadata
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize OrganisationService."""
        repository = OrganisationRepository(db)
        super().__init__(repository, db)
    
    async def search_organizations(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Organisation]:
        """
        Search organizations by name.
        
        Args:
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching organizations
        """
        return await self.repository.search(query, skip=skip, limit=limit)
    
    async def get_by_country(
        self,
        pays: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Organisation]:
        """
        Get organizations by country.

        Args:
            pays: Country code (ISO 3166-1 alpha-3, e.g., 'USA', 'FRA')
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of organizations in the country
        """
        return await self.repository.get_by_country(pays, skip=skip, limit=limit)
    
    async def get_top_by_publications(
        self,
        limit: int = 100,
        min_publications: int = 10
    ) -> List[Organisation]:
        """
        Get top organizations by publication count.
        
        Args:
            limit: Maximum number of organizations to return
            min_publications: Minimum publication threshold
            
        Returns:
            List of top organizations
        """
        stmt = (
            select(Organisation)
            .where(Organisation.nombre_publications >= min_publications)
            .order_by(Organisation.nombre_publications.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_top_by_ranking(
        self,
        limit: int = 100
    ) -> List[Organisation]:
        """
        Get top organizations by world ranking.
        
        Args:
            limit: Maximum number of organizations to return
            
        Returns:
            List of top-ranked organizations
        """
        stmt = (
            select(Organisation)
            .where(Organisation.ranking_mondial.isnot(None))
            .order_by(Organisation.ranking_mondial.asc())
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def _validate_create(self, obj_in: Dict[str, Any]) -> None:
        """
        Validate organization data before creation.
        
        Checks:
        - Name uniqueness
        - Valid organization type
        
        Args:
            obj_in: Organization data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check name uniqueness
        if 'nom' in obj_in:
            existing = await self.repository.get_by_nom(obj_in['nom'])
            if existing:
                raise ValueError(f"Organization with name '{obj_in['nom']}' already exists")
        
        # Validate type if provided
        if 'type_organisation' in obj_in:
            valid_types = [
                'university', 'company', 'research_center',
                'think_tank', 'government', 'ngo', 'other'
            ]
            if obj_in['type_organisation'] not in valid_types:
                raise ValueError(f"Invalid organization type. Must be one of: {valid_types}")
    
    async def _validate_update(
        self,
        entity_id: UUID,
        obj_in: Dict[str, Any]
    ) -> None:
        """
        Validate organization data before update.

        Checks:
        - Name uniqueness if being updated (excluding current organization)
        - Valid organization type

        Args:
            entity_id: Organization UUID being updated
            obj_in: Organization data to validate

        Raises:
            ValueError: If validation fails
        """
        # Check name uniqueness if changing
        if 'nom' in obj_in:
            existing = await self.repository.get_by_nom(obj_in['nom'])
            if existing and existing.id != entity_id:
                raise ValueError(f"Organization with name '{obj_in['nom']}' already exists")

        # Validate type if provided
        if 'type_organisation' in obj_in:
            valid_types = [
                'university', 'company', 'research_center',
                'think_tank', 'government', 'ngo', 'other'
            ]
            if obj_in['type_organisation'] not in valid_types:
                raise ValueError(f"Invalid organization type. Must be one of: {valid_types}")
