"""
AuteurRepository - Repository spécialisé pour les auteurs/chercheurs

Méthodes spécialisées pour recherche par ORCID, Semantic Scholar ID, nom, et h-index.
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload

from app.models import Auteur
from .base_repository import BaseRepository


class AuteurRepository(BaseRepository[Auteur]):
    """
    Repository pour les auteurs/chercheurs en IA.
    
    Fournit des méthodes spécialisées pour :
    - Recherche par ORCID (identifiant international unique)
    - Recherche par Semantic Scholar ID (Phase 3)
    - Recherche par nom (fuzzy search)
    - Filtrage par plage de h-index
    - Eager loading des publications et affiliations
    
    Example:
        >>> repository = AuteurRepository(db_session)
        >>> 
        >>> # Recherche par ORCID
        >>> auteur = await repository.get_by_orcid("0000-0002-1234-5678")
        >>> 
        >>> # Top auteurs par h-index
        >>> top_authors = await repository.get_by_h_index_range(min_h=50, max_h=200)
        >>> 
        >>> # Auteur avec toutes ses publications
        >>> auteur_full = await repository.get_with_publications(auteur_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialise le repository avec une session DB.
        
        Args:
            db: Session de base de données asynchrone
        """
        super().__init__(Auteur, db)
    
    async def get_by_orcid(self, orcid: str) -> Optional[Auteur]:
        """
        Récupère un auteur par son identifiant ORCID.
        
        ORCID (Open Researcher and Contributor ID) est un identifiant unique
        et persistant pour les chercheurs.
        
        Args:
            orcid: Identifiant ORCID (format: XXXX-XXXX-XXXX-XXXX)
            
        Returns:
            Auteur si trouvé, None sinon
            
        Example:
            >>> auteur = await repository.get_by_orcid("0000-0002-1234-5678")
            >>> if auteur:
            ...     print(f"{auteur.nom} {auteur.prenom}")
        """
        stmt = select(Auteur).where(Auteur.orcid == orcid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_semantic_scholar_id(self, ss_id: str) -> Optional[Auteur]:
        """
        Récupère un auteur par son identifiant Semantic Scholar.
        
        CRITIQUE pour Phase 3 : Utilisé pour lier les auteurs avec l'API
        Semantic Scholar et enrichir leurs métriques (h-index, citations).
        
        Args:
            ss_id: Identifiant Semantic Scholar
            
        Returns:
            Auteur si trouvé, None sinon
            
        Example:
            >>> auteur = await repository.get_by_semantic_scholar_id("123456789")
        """
        stmt = select(Auteur).where(Auteur.semantic_scholar_id == ss_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_by_name(
        self, 
        name: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Auteur]:
        """
        Recherche des auteurs par nom (nom ou prénom).
        
        Utilise ILIKE pour recherche case-insensitive sur nom ET prénom.
        
        Args:
            name: Terme de recherche (peut matcher nom ou prénom)
            skip: Nombre d'enregistrements à sauter
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des auteurs correspondants
            
        Example:
            >>> # Recherche "Bengio"
            >>> results = await repository.search_by_name("Bengio")
            >>> 
            >>> # Recherche "Yoshua"
            >>> results = await repository.search_by_name("Yoshua")
        """
        search_pattern = f"%{name}%"
        stmt = (
            select(Auteur)
            .where(
                or_(
                    Auteur.nom.ilike(search_pattern),
                    Auteur.prenom.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_publications(self, auteur_id: UUID) -> Optional[Auteur]:
        """
        Récupère un auteur avec toutes ses publications en eager loading.
        
        Évite le problème N+1 queries.
        
        Args:
            auteur_id: UUID de l'auteur
            
        Returns:
            Auteur avec relation 'publications' chargée, None si non trouvé
            
        Example:
            >>> auteur = await repository.get_with_publications(auteur_id)
            >>> if auteur:
            ...     print(f"Nombre de publications: {len(auteur.publications)}")
            ...     for pub_auteur in auteur.publications:
            ...         print(f"- {pub_auteur.publication.titre}")
        """
        stmt = (
            select(Auteur)
            .where(Auteur.id == auteur_id)
            .options(selectinload(Auteur.publications))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_h_index_range(
        self, 
        min_h: int = 0, 
        max_h: int = 1000
    ) -> List[Auteur]:
        """
        Récupère les auteurs dans une plage de h-index.
        
        Utile pour identifier les chercheurs influents.
        Tri par h-index décroissant.
        
        Args:
            min_h: H-index minimum (inclus)
            max_h: H-index maximum (inclus)
            
        Returns:
            Liste des auteurs dans cette plage, triés par h-index DESC
            
        Example:
            >>> # Chercheurs très influents (h-index 50+)
            >>> top_researchers = await repository.get_by_h_index_range(
            ...     min_h=50,
            ...     max_h=200
            ... )
            >>> for auteur in top_researchers:
            ...     print(f"{auteur.nom}: h-index={auteur.h_index}")
        """
        stmt = (
            select(Auteur)
            .where(
                and_(
                    Auteur.h_index >= min_h,
                    Auteur.h_index <= max_h
                )
            )
            .order_by(desc(Auteur.h_index))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_top_by_h_index(self, limit: int = 100) -> List[Auteur]:
        """
        Récupère les auteurs avec le h-index le plus élevé.
        
        Args:
            limit: Nombre d'auteurs à retourner
            
        Returns:
            Liste des top auteurs triés par h-index DESC
            
        Example:
            >>> top_10 = await repository.get_top_by_h_index(limit=10)
            >>> for i, auteur in enumerate(top_10, 1):
            ...     print(f"{i}. {auteur.nom}: h-index={auteur.h_index}")
        """
        stmt = (
            select(Auteur)
            .order_by(desc(Auteur.h_index))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_affiliations(self, auteur_id: UUID) -> Optional[Auteur]:
        """
        Récupère un auteur avec ses affiliations en eager loading.
        
        Args:
            auteur_id: UUID de l'auteur
            
        Returns:
            Auteur avec relation 'affiliations' chargée
            
        Example:
            >>> auteur = await repository.get_with_affiliations(auteur_id)
            >>> if auteur:
            ...     for affiliation in auteur.affiliations:
            ...         org = affiliation.organisation
            ...         print(f"{org.nom} ({affiliation.poste})")
        """
        stmt = (
            select(Auteur)
            .where(Auteur.id == auteur_id)
            .options(selectinload(Auteur.affiliations))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def count_by_h_index_threshold(self, threshold: int) -> int:
        """
        Compte le nombre d'auteurs avec h-index >= threshold.
        
        Args:
            threshold: Seuil de h-index
            
        Returns:
            Nombre d'auteurs au-dessus du seuil
            
        Example:
            >>> influential = await repository.count_by_h_index_threshold(50)
            >>> print(f"Chercheurs avec h-index >= 50: {influential}")
        """
        stmt = (
            select(func.count())
            .select_from(Auteur)
            .where(Auteur.h_index >= threshold)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
