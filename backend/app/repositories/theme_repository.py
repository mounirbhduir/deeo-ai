"""
ThemeRepository - Repository spécialisé pour les thèmes de recherche IA

Méthodes spécialisées pour hiérarchie taxonomique, recherche et classement par usage.
"""
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload

from app.models import Theme
from .base_repository import BaseRepository


class ThemeRepository(BaseRepository[Theme]):
    """
    Repository pour les thèmes de recherche IA organisés en hiérarchie.
    
    Fournit des méthodes spécialisées pour :
    - Recherche par nom (label)
    - Navigation hiérarchique (parent/enfants)
    - Thèmes les plus utilisés (par nombre de publications)
    - Eager loading des publications associées
    - Recherche par niveau hiérarchique
    
    Example:
        >>> repository = ThemeRepository(db_session)
        >>> 
        >>> # Recherche par nom
        >>> ml_theme = await repository.get_by_nom("Machine Learning")
        >>> 
        >>> # Top thèmes par usage
        >>> top_themes = await repository.get_most_used(limit=20)
        >>> 
        >>> # Thèmes de niveau 1 (disciplines majeures)
        >>> disciplines = await repository.get_by_level(1)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialise le repository avec une session DB.
        
        Args:
            db: Session de base de données asynchrone
        """
        super().__init__(Theme, db)
    
    async def get_by_nom(self, nom: str) -> Optional[Theme]:
        """
        Récupère un thème par son label exact.
        
        Args:
            nom: Label exact du thème (ex: "Machine Learning")
            
        Returns:
            Theme si trouvé, None sinon
            
        Example:
            >>> theme = await repository.get_by_nom("Machine Learning")
            >>> if theme:
            ...     print(f"Niveau: {theme.niveau_hierarchie}")
        """
        stmt = select(Theme).where(Theme.label == nom)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Theme]:
        """
        Recherche fuzzy sur le label et la description.
        
        Args:
            query: Terme de recherche
            skip: Nombre d'enregistrements à sauter
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des thèmes correspondants
            
        Example:
            >>> results = await repository.search("learning")
            >>> for theme in results:
            ...     print(f"{theme.label} (niveau {theme.niveau_hierarchie})")
        """
        search_pattern = f"%{query}%"
        stmt = (
            select(Theme)
            .where(
                or_(
                    Theme.label.ilike(search_pattern),
                    Theme.description.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_publications(self, theme_id: UUID) -> Optional[Theme]:
        """
        Récupère un thème avec ses publications associées.
        
        Args:
            theme_id: UUID du thème
            
        Returns:
            Theme avec relation 'publications' chargée
            
        Example:
            >>> theme = await repository.get_with_publications(theme_id)
            >>> if theme:
            ...     print(f"Publications: {len(theme.publications)}")
            ...     for pub_theme in theme.publications:
            ...         print(f"- {pub_theme.publication.titre}")
        """
        stmt = (
            select(Theme)
            .where(Theme.id == theme_id)
            .options(selectinload(Theme.publications))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_most_used(self, limit: int = 20) -> List[Tuple[Theme, int]]:
        """
        Récupère les thèmes les plus utilisés (par nombre de publications).
        
        Utilise le champ calculé 'nombre_publications'.
        
        Args:
            limit: Nombre de thèmes à retourner
            
        Returns:
            Liste de tuples (theme, count) triée par count DESC
            
        Example:
            >>> top_themes = await repository.get_most_used(limit=10)
            >>> for i, (theme, count) in enumerate(top_themes, 1):
            ...     print(f"{i}. {theme.label}: {count} publications")
        """
        stmt = (
            select(Theme)
            .order_by(desc(Theme.nombre_publications))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        themes = list(result.scalars().all())
        
        return [(theme, theme.nombre_publications) for theme in themes]
    
    async def get_by_level(self, niveau: int) -> List[Theme]:
        """
        Récupère tous les thèmes d'un niveau hiérarchique donné.
        
        Args:
            niveau: Niveau hiérarchique (0 = racine, 1 = disciplines, etc.)
            
        Returns:
            Liste des thèmes à ce niveau
            
        Example:
            >>> # Disciplines majeures (niveau 1)
            >>> disciplines = await repository.get_by_level(1)
            >>> 
            >>> # Sous-domaines (niveau 2)
            >>> subdomains = await repository.get_by_level(2)
        """
        stmt = (
            select(Theme)
            .where(Theme.niveau_hierarchie == niveau)
            .order_by(Theme.label)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_children(self, parent_id: UUID) -> List[Theme]:
        """
        Récupère tous les thèmes enfants d'un thème parent.
        
        Args:
            parent_id: UUID du thème parent
            
        Returns:
            Liste des thèmes enfants
            
        Example:
            >>> ml_theme = await repository.get_by_nom("Machine Learning")
            >>> if ml_theme:
            ...     children = await repository.get_children(ml_theme.id)
            ...     for child in children:
            ...         print(f"- {child.label}")
        """
        stmt = (
            select(Theme)
            .where(Theme.parent_id == parent_id)
            .order_by(Theme.label)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_root_themes(self) -> List[Theme]:
        """
        Récupère tous les thèmes racine (sans parent).
        
        Returns:
            Liste des thèmes racine
            
        Example:
            >>> roots = await repository.get_root_themes()
            >>> for root in roots:
            ...     print(f"- {root.label} (niveau {root.niveau_hierarchie})")
        """
        stmt = (
            select(Theme)
            .where(Theme.parent_id.is_(None))
            .order_by(Theme.label)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_hierarchy(self, theme_id: UUID) -> Optional[Theme]:
        """
        Récupère un thème avec son parent et ses enfants chargés.
        
        Args:
            theme_id: UUID du thème
            
        Returns:
            Theme avec relations 'parent' et 'enfants' chargées
            
        Example:
            >>> theme = await repository.get_with_hierarchy(theme_id)
            >>> if theme:
            ...     if theme.parent:
            ...         print(f"Parent: {theme.parent.label}")
            ...     print(f"Enfants: {len(theme.enfants)}")
        """
        stmt = (
            select(Theme)
            .where(Theme.id == theme_id)
            .options(
                selectinload(Theme.parent),
                selectinload(Theme.enfants)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def count_by_level(self, niveau: int) -> int:
        """
        Compte le nombre de thèmes à un niveau hiérarchique donné.
        
        Args:
            niveau: Niveau hiérarchique
            
        Returns:
            Nombre de thèmes à ce niveau
            
        Example:
            >>> level1_count = await repository.count_by_level(1)
            >>> print(f"Disciplines (niveau 1): {level1_count}")
        """
        stmt = (
            select(func.count())
            .select_from(Theme)
            .where(Theme.niveau_hierarchie == niveau)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
    
    async def search_by_path(self, path_fragment: str) -> List[Theme]:
        """
        Recherche des thèmes par fragment de chemin hiérarchique.
        
        Args:
            path_fragment: Fragment de chemin (ex: "AI/ML")
            
        Returns:
            Liste des thèmes dont le chemin contient ce fragment
            
        Example:
            >>> # Tous les sous-domaines de Machine Learning
            >>> ml_subdomains = await repository.search_by_path("Machine Learning/")
        """
        search_pattern = f"%{path_fragment}%"
        stmt = (
            select(Theme)
            .where(Theme.chemin_hierarchie.ilike(search_pattern))
            .order_by(Theme.niveau_hierarchie, Theme.label)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
