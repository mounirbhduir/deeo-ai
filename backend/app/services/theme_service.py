"""Theme service with business logic."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.theme import Theme
from app.repositories.theme_repository import ThemeRepository
from app.services.base_service import BaseService


class ThemeService(BaseService[Theme, ThemeRepository]):
    """
    Service for Theme entity with business logic.
    
    Provides methods for:
    - Managing hierarchical themes
    - Navigating theme tree
    - Theme-based statistics
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize ThemeService."""
        repository = ThemeRepository(db)
        super().__init__(repository, db)
    
    async def get_root_themes(self) -> List[Theme]:
        """
        Get all root themes (level 0, no parent).
        
        Returns:
            List of root themes
        """
        return await self.repository.get_root_themes()
    
    async def get_children(self, theme_id: UUID) -> List[Theme]:
        """
        Get direct children of a theme.

        Args:
            theme_id: Parent theme UUID

        Returns:
            List of child themes
        """
        return await self.repository.get_children(theme_id)
    
    async def get_by_level(
        self,
        niveau: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Theme]:
        """
        Get themes at a specific hierarchical level.
        
        Args:
            niveau: Hierarchical level (0 = root)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of themes at the specified level
        """
        return await self.repository.get_by_level(niveau, skip=skip, limit=limit)
    
    async def get_popular_themes(
        self,
        limit: int = 20,
        min_publications: int = 10
    ) -> List[Theme]:
        """
        Get most popular themes by publication count.

        Args:
            limit: Maximum number of themes to return
            min_publications: Minimum publication threshold

        Returns:
            List of popular themes
        """
        stmt = (
            select(Theme)
            .where(Theme.nombre_publications >= min_publications)
            .order_by(Theme.nombre_publications.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_theme_hierarchy(self, theme_id: UUID) -> List[Theme]:
        """
        Get full hierarchy path from root to theme.

        Args:
            theme_id: Theme UUID

        Returns:
            List of themes from root to specified theme
        """
        theme = await self.get(theme_id)
        if not theme:
            return []

        hierarchy = [theme]
        current = theme

        # Walk up the tree to root
        while current.parent_id:
            parent = await self.get(current.parent_id)
            if not parent:
                break
            hierarchy.insert(0, parent)
            current = parent

        return hierarchy
    
    async def search_themes(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Theme]:
        """
        Search themes by label or description.

        Args:
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching themes
        """
        stmt = (
            select(Theme)
            .where(Theme.label.ilike(f"%{query}%"))
            .limit(limit)
            .offset(skip)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def _validate_create(self, obj_in: Dict[str, Any]) -> None:
        """
        Validate theme data before creation.
        
        Checks:
        - Label uniqueness at same level
        - Parent exists if parent_id provided
        - Hierarchical level constraints
        
        Args:
            obj_in: Theme data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Validate hierarchical level
        if 'niveau_hierarchie' in obj_in:
            niveau = obj_in['niveau_hierarchie']
            if niveau < 0 or niveau > 10:
                raise ValueError("Hierarchical level must be between 0 and 10")
        
        # Validate parent exists if provided
        if 'parent_id' in obj_in and obj_in['parent_id']:
            parent = await self.get(obj_in['parent_id'])
            if not parent:
                raise ValueError(f"Parent theme with ID {obj_in['parent_id']} not found")
            
            # Ensure child level is parent level + 1
            if 'niveau_hierarchie' in obj_in:
                expected_level = parent.niveau_hierarchie + 1
                if obj_in['niveau_hierarchie'] != expected_level:
                    raise ValueError(
                        f"Child theme level must be {expected_level} "
                        f"(parent level {parent.niveau_hierarchie} + 1)"
                    )
    
    async def _validate_update(
        self,
        entity_id: UUID,
        obj_in: Dict[str, Any]
    ) -> None:
        """
        Validate theme data before update.

        Checks:
        - Cannot change parent to create circular reference
        - Hierarchical level constraints

        Args:
            entity_id: Theme UUID being updated
            obj_in: Theme data to validate

        Raises:
            ValueError: If validation fails
        """
        # Validate hierarchical level if provided
        if 'niveau_hierarchie' in obj_in:
            niveau = obj_in['niveau_hierarchie']
            if niveau < 0 or niveau > 10:
                raise ValueError("Hierarchical level must be between 0 and 10")

        # Validate parent if changing
        if 'parent_id' in obj_in and obj_in['parent_id']:
            # IMPORTANT: Check circular reference BEFORE checking if parent exists
            # This prevents error when parent_id == entity_id and parent doesn't exist yet
            if obj_in['parent_id'] == entity_id:
                raise ValueError("Theme cannot be its own parent")

            # Now check if parent exists
            parent = await self.get(obj_in['parent_id'])
            if not parent:
                raise ValueError(f"Parent theme with ID {obj_in['parent_id']} not found")

            # TODO: Check for circular references in hierarchy
            # This would require traversing the tree to ensure entity_id
            # doesn't appear in parent's ancestry
