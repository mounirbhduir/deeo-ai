"""
OrganisationRepository - Repository spécialisé pour les organisations

Méthodes spécialisées pour recherche par nom, pays, et classement par publications.
"""
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload

from app.models import Organisation
from app.models.enums import TypeOrganisationEnum
from .base_repository import BaseRepository


class OrganisationRepository(BaseRepository[Organisation]):
    """
    Repository pour les organisations (universités, entreprises, centres de recherche).
    
    Fournit des méthodes spécialisées pour :
    - Recherche par nom exact
    - Recherche full-text (fuzzy)
    - Filtrage par pays
    - Filtrage par type d'organisation
    - Top organisations par nombre de publications
    - Eager loading des chercheurs affiliés
    
    Example:
        >>> repository = OrganisationRepository(db_session)
        >>> 
        >>> # Recherche par nom
        >>> mit = await repository.get_by_nom("MIT")
        >>> 
        >>> # Top universités
        >>> top_unis = await repository.get_top_by_publications_count(limit=10)
        >>> 
        >>> # Organisations françaises
        >>> fr_orgs = await repository.get_by_country("FRA")
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialise le repository avec une session DB.
        
        Args:
            db: Session de base de données asynchrone
        """
        super().__init__(Organisation, db)
    
    async def get_by_nom(self, nom: str) -> Optional[Organisation]:
        """
        Récupère une organisation par son nom exact.
        
        Recherche case-sensitive sur le nom complet.
        
        Args:
            nom: Nom exact de l'organisation
            
        Returns:
            Organisation si trouvée, None sinon
            
        Example:
            >>> org = await repository.get_by_nom("Massachusetts Institute of Technology")
            >>> if org:
            ...     print(f"Nom court: {org.nom_court}")
        """
        stmt = select(Organisation).where(Organisation.nom == nom)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search(
        self, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Organisation]:
        """
        Recherche fuzzy sur nom et nom_court.
        
        Utilise ILIKE pour recherche case-insensitive.
        
        Args:
            query: Terme de recherche
            skip: Nombre d'enregistrements à sauter
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des organisations correspondantes
            
        Example:
            >>> # Recherche "Stanford"
            >>> results = await repository.search("Stanford")
            >>> 
            >>> # Recherche "Google"
            >>> results = await repository.search("Google")
        """
        search_pattern = f"%{query}%"
        stmt = (
            select(Organisation)
            .where(
                or_(
                    Organisation.nom.ilike(search_pattern),
                    Organisation.nom_court.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_country(
        self, 
        pays: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Organisation]:
        """
        Récupère les organisations d'un pays donné.
        
        Args:
            pays: Code pays ISO 3166-1 alpha-3 (ex: "USA", "FRA", "GBR")
            skip: Nombre d'enregistrements à sauter
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des organisations du pays
            
        Example:
            >>> # Organisations américaines
            >>> usa_orgs = await repository.get_by_country("USA", limit=50)
            >>> 
            >>> # Organisations françaises
            >>> fra_orgs = await repository.get_by_country("FRA")
        """
        stmt = (
            select(Organisation)
            .where(Organisation.pays == pays)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_type(
        self,
        type_org: TypeOrganisationEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[Organisation]:
        """
        Récupère les organisations par type.
        
        Args:
            type_org: Type d'organisation (UNIVERSITY, COMPANY, etc.)
            skip: Nombre d'enregistrements à sauter
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des organisations du type spécifié
            
        Example:
            >>> # Toutes les universités
            >>> universities = await repository.get_by_type(
            ...     TypeOrganisationEnum.UNIVERSITY
            ... )
            >>> 
            >>> # Toutes les entreprises
            >>> companies = await repository.get_by_type(
            ...     TypeOrganisationEnum.COMPANY
            ... )
        """
        stmt = (
            select(Organisation)
            .where(Organisation.type_organisation == type_org)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_with_publications(
        self, 
        org_id: UUID
    ) -> Optional[Organisation]:
        """
        Récupère une organisation avec ses chercheurs affiliés.
        
        Note: Les publications sont liées via les auteurs, pas directement
        à l'organisation. Pour obtenir les publications d'une organisation,
        il faut passer par les affiliations des auteurs.
        
        Args:
            org_id: UUID de l'organisation
            
        Returns:
            Organisation avec relation 'affiliations' chargée
            
        Example:
            >>> org = await repository.get_with_publications(org_id)
            >>> if org:
            ...     for affiliation in org.affiliations:
            ...         auteur = affiliation.auteur
            ...         print(f"Chercheur: {auteur.nom}")
        """
        stmt = (
            select(Organisation)
            .where(Organisation.id == org_id)
            .options(selectinload(Organisation.affiliations))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_top_by_publications_count(
        self, 
        limit: int = 10
    ) -> List[Tuple[Organisation, int]]:
        """
        Récupère les organisations avec le plus de publications.
        
        Retourne une liste de tuples (Organisation, nombre_publications).
        Utilise le champ calculé 'nombre_publications' dans la table.
        
        Args:
            limit: Nombre d'organisations à retourner
            
        Returns:
            Liste de tuples (organisation, count) triée par count DESC
            
        Example:
            >>> top_orgs = await repository.get_top_by_publications_count(limit=10)
            >>> for i, (org, count) in enumerate(top_orgs, 1):
            ...     print(f"{i}. {org.nom}: {count} publications")
        """
        stmt = (
            select(Organisation)
            .order_by(desc(Organisation.nombre_publications))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        organisations = list(result.scalars().all())
        
        # Retourner tuples (Organisation, nombre_publications)
        return [(org, org.nombre_publications) for org in organisations]
    
    async def get_by_ranking_range(
        self,
        min_rank: int = 1,
        max_rank: int = 100
    ) -> List[Organisation]:
        """
        Récupère les organisations dans une plage de classement mondial.
        
        Args:
            min_rank: Rang minimum (1 = meilleur)
            max_rank: Rang maximum
            
        Returns:
            Liste des organisations dans cette plage, triées par rang
            
        Example:
            >>> # Top 50 universités mondiales
            >>> top_50 = await repository.get_by_ranking_range(1, 50)
        """
        stmt = (
            select(Organisation)
            .where(
                and_(
                    Organisation.ranking_mondial.isnot(None),
                    Organisation.ranking_mondial >= min_rank,
                    Organisation.ranking_mondial <= max_rank
                )
            )
            .order_by(Organisation.ranking_mondial)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def count_by_type(self, type_org: TypeOrganisationEnum) -> int:
        """
        Compte le nombre d'organisations par type.
        
        Args:
            type_org: Type d'organisation
            
        Returns:
            Nombre d'organisations de ce type
            
        Example:
            >>> universities_count = await repository.count_by_type(
            ...     TypeOrganisationEnum.UNIVERSITY
            ... )
            >>> print(f"Nombre d'universités: {universities_count}")
        """
        stmt = (
            select(func.count())
            .select_from(Organisation)
            .where(Organisation.type_organisation == type_org)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
    
    async def count_by_country(self, pays: str) -> int:
        """
        Compte le nombre d'organisations par pays.
        
        Args:
            pays: Code pays ISO 3166-1 alpha-3
            
        Returns:
            Nombre d'organisations dans ce pays
            
        Example:
            >>> usa_count = await repository.count_by_country("USA")
            >>> print(f"Organisations américaines: {usa_count}")
        """
        stmt = (
            select(func.count())
            .select_from(Organisation)
            .where(Organisation.pays == pays)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
