"""
PublicationRepository - Repository spécialisé pour les publications

Méthodes spécialisées pour recherche par DOI, arXiv ID, statut, full-text search, etc.
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.models import Publication
from app.models.enums import StatusPublicationEnum
from .base_repository import BaseRepository


class PublicationRepository(BaseRepository[Publication]):
    """
    Repository pour les publications scientifiques.
    
    Fournit des méthodes spécialisées pour :
    - Recherche par DOI (critique pour Phase 3 - Semantic Scholar)
    - Recherche par arXiv ID
    - Recherche par statut d'enrichissement
    - Recherche full-text sur titre et résumé
    - Eager loading des relations (auteurs, organisations)
    - Tri par date de publication
    
    Example:
        >>> repository = PublicationRepository(db_session)
        >>> 
        >>> # Recherche par DOI
        >>> pub = await repository.get_by_doi("10.1234/test")
        >>> 
        >>> # Recherche full-text
        >>> results = await repository.search("deep learning", limit=10)
        >>> 
        >>> # Publications avec auteurs chargés
        >>> pub_with_authors = await repository.get_with_authors(publication_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialise le repository avec une session DB.
        
        Args:
            db: Session de base de données asynchrone
        """
        super().__init__(Publication, db)
    
    async def get_by_doi(self, doi: str) -> Optional[Publication]:
        """
        Récupère une publication par son DOI.
        
        CRITIQUE pour Phase 3 : Le DOI est utilisé pour interroger l'API
        Semantic Scholar et enrichir les métadonnées.
        
        Args:
            doi: Digital Object Identifier (ex: "10.1234/test.2024")
            
        Returns:
            Publication si trouvée, None sinon
            
        Example:
            >>> pub = await repository.get_by_doi("10.1234/test")
            >>> if pub:
            ...     print(f"Trouvé: {pub.titre}")
        """
        stmt = select(Publication).where(Publication.doi == doi)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_arxiv_id(self, arxiv_id: str) -> Optional[Publication]:
        """
        Récupère une publication par son identifiant arXiv.
        
        CRITIQUE pour Phase 3 : Alternative au DOI pour les preprints arXiv.
        
        Args:
            arxiv_id: Identifiant arXiv (ex: "2024.12345")
            
        Returns:
            Publication si trouvée, None sinon
            
        Example:
            >>> pub = await repository.get_by_arxiv_id("2024.12345")
        """
        stmt = select(Publication).where(Publication.arxiv_id == arxiv_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_status(
        self, 
        status: StatusPublicationEnum, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Publication]:
        """
        Récupère les publications par statut d'enrichissement.
        
        Utilisé en Phase 3 par le pipeline d'enrichissement pour identifier
        les publications à traiter.
        
        Args:
            status: Statut à filtrer (PUBLISHED, PENDING_ENRICHMENT, ENRICHED, etc.)
            skip: Nombre d'enregistrements à sauter
            limit: Nombre maximum d'enregistrements
            
        Returns:
            Liste des publications avec ce statut
            
        Example:
            >>> # Récupérer publications à enrichir
            >>> pubs = await repository.get_by_status(
            ...     StatusPublicationEnum.PENDING_ENRICHMENT,
            ...     limit=50
            ... )
        """
        stmt = (
            select(Publication)
            .where(Publication.status == status)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def search(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Publication]:
        """
        Recherche full-text sur titre et résumé.
        
        Utilise ILIKE pour recherche case-insensitive.
        En production, PostgreSQL full-text search (tsvector) serait plus performant.
        
        Args:
            query: Terme(s) de recherche
            skip: Nombre d'enregistrements à sauter
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des publications correspondantes
            
        Example:
            >>> results = await repository.search("transformer attention", limit=20)
            >>> for pub in results:
            ...     print(pub.titre)
        """
        search_pattern = f"%{query}%"
        stmt = (
            select(Publication)
            .where(
                or_(
                    Publication.titre.ilike(search_pattern),
                    Publication.abstract.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_authors(self, publication_id: UUID) -> Optional[Publication]:
        """
        Récupère une publication avec ses auteurs en eager loading.
        
        Évite le problème N+1 queries en chargeant les auteurs en une seule requête.
        
        Args:
            publication_id: UUID de la publication
            
        Returns:
            Publication avec relation 'auteurs' chargée, None si non trouvée
            
        Example:
            >>> pub = await repository.get_with_authors(pub_id)
            >>> if pub:
            ...     for pub_auteur in pub.auteurs:
            ...         print(f"Auteur: {pub_auteur.auteur.nom}")
        """
        stmt = (
            select(Publication)
            .where(Publication.id == publication_id)
            .options(selectinload(Publication.auteurs))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_organizations(
        self, 
        publication_id: UUID
    ) -> Optional[Publication]:
        """
        Récupère une publication avec ses organisations via les affiliations des auteurs.
        
        Note: Les publications n'ont pas de relation directe organisations dans le modèle actuel.
        Pour obtenir les organisations, il faut passer par les auteurs et leurs affiliations.
        
        Args:
            publication_id: UUID de la publication
            
        Returns:
            Publication avec auteurs et leurs affiliations chargées
            
        Example:
            >>> pub = await repository.get_with_organizations(pub_id)
            >>> if pub:
            ...     for pub_auteur in pub.auteurs:
            ...         for affiliation in pub_auteur.auteur.affiliations:
            ...             print(f"Org: {affiliation.organisation.nom}")
        """
        stmt = (
            select(Publication)
            .where(Publication.id == publication_id)
            .options(
                selectinload(Publication.auteurs)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_recent(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Publication]:
        """
        Récupère les publications les plus récentes.
        
        Tri par date_publication décroissante (plus récentes en premier).
        
        Args:
            skip: Nombre d'enregistrements à sauter
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des publications triées par date décroissante
            
        Example:
            >>> recent_pubs = await repository.get_recent(limit=10)
            >>> for pub in recent_pubs:
            ...     print(f"{pub.date_publication}: {pub.titre}")
        """
        stmt = (
            select(Publication)
            .order_by(desc(Publication.date_publication))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def count_by_status(self, status: StatusPublicationEnum) -> int:
        """
        Compte le nombre de publications par statut.
        
        Utile pour monitoring du pipeline Phase 3.
        
        Args:
            status: Statut à compter
            
        Returns:
            Nombre de publications avec ce statut
            
        Example:
            >>> pending = await repository.count_by_status(
            ...     StatusPublicationEnum.PENDING_ENRICHMENT
            ... )
            >>> print(f"Publications à enrichir: {pending}")
        """
        from sqlalchemy import func, select
        
        stmt = (
            select(func.count())
            .select_from(Publication)
            .where(Publication.status == status)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
