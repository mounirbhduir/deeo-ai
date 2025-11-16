"""
BaseRepository - Repository générique avec opérations CRUD de base

Utilise le pattern Generic[T] pour être réutilisable avec n'importe quel modèle SQLAlchemy.
"""
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


# TypeVar pour rendre BaseRepository générique
ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Repository de base avec opérations CRUD génériques.
    
    Ce repository fournit les méthodes de base pour interagir avec la base de données
    de manière asynchrone. Tous les repositories spécialisés héritent de cette classe.
    
    Attributes:
        model: La classe du modèle SQLAlchemy
        db: Session de base de données asynchrone
        
    Example:
        >>> class PublicationRepository(BaseRepository[Publication]):
        ...     def __init__(self, db: AsyncSession):
        ...         super().__init__(Publication, db)
        ...
        >>> repository = PublicationRepository(db_session)
        >>> publication = await repository.get(publication_id)
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialise le repository avec un modèle et une session DB.
        
        Args:
            model: Classe du modèle SQLAlchemy (ex: Publication, Auteur)
            db: Session de base de données asynchrone
        """
        self.model = model
        self.db = db
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Crée une nouvelle instance dans la base de données.
        
        Args:
            obj_in: Dictionnaire contenant les données à insérer
            
        Returns:
            L'instance créée avec son ID généré
            
        Raises:
            ValueError: Si une contrainte d'intégrité est violée
            
        Example:
            >>> data = {"titre": "Test", "doi": "10.1234/test"}
            >>> publication = await repository.create(data)
            >>> print(publication.id)  # UUID auto-généré
        """
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Integrity constraint violated: {str(e)}") from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise ValueError(f"Database error: {str(e)}") from e
    
    async def get(self, id: UUID) -> Optional[ModelType]:
        """
        Récupère une instance par son ID UUID.
        
        Args:
            id: UUID de l'instance à récupérer
            
        Returns:
            L'instance si trouvée, None sinon
            
        Example:
            >>> publication = await repository.get(publication_id)
            >>> if publication:
            ...     print(publication.titre)
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """
        Récupère plusieurs instances avec pagination.
        
        Args:
            skip: Nombre d'enregistrements à sauter (pour pagination)
            limit: Nombre maximum d'enregistrements à retourner
            
        Returns:
            Liste des instances trouvées (peut être vide)
            
        Example:
            >>> # Récupérer les 100 premières publications
            >>> publications = await repository.get_multi(skip=0, limit=100)
            >>> 
            >>> # Récupérer la 2e page (publications 100-199)
            >>> publications_page2 = await repository.get_multi(skip=100, limit=100)
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, id: UUID, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """
        Met à jour une instance existante.
        
        Args:
            id: UUID de l'instance à mettre à jour
            obj_in: Dictionnaire contenant les champs à mettre à jour
            
        Returns:
            L'instance mise à jour si trouvée, None sinon
            
        Example:
            >>> updates = {"titre": "Nouveau titre", "nombre_citations": 42}
            >>> publication = await repository.update(publication_id, updates)
            >>> if publication:
            ...     print(publication.titre)  # "Nouveau titre"
        """
        db_obj = await self.get(id)
        if db_obj:
            try:
                for field, value in obj_in.items():
                    setattr(db_obj, field, value)
                await self.db.commit()
                await self.db.refresh(db_obj)
                return db_obj
            except IntegrityError as e:
                await self.db.rollback()
                raise ValueError(f"Integrity constraint violated: {str(e)}") from e
            except SQLAlchemyError as e:
                await self.db.rollback()
                raise ValueError(f"Database error: {str(e)}") from e
        return None
    
    async def delete(self, id: UUID) -> bool:
        """
        Supprime une instance (suppression physique).
        
        Note: Contrairement au prompt initial qui suggérait un soft delete,
        cette méthode fait une suppression physique. Le soft delete peut être
        implémenté dans les repositories spécialisés si nécessaire.
        
        Args:
            id: UUID de l'instance à supprimer
            
        Returns:
            True si supprimé avec succès, False si non trouvé
            
        Example:
            >>> success = await repository.delete(publication_id)
            >>> if success:
            ...     print("Publication supprimée")
        """
        db_obj = await self.get(id)
        if db_obj:
            try:
                await self.db.delete(db_obj)
                await self.db.commit()
                return True
            except SQLAlchemyError as e:
                await self.db.rollback()
                raise ValueError(f"Database error: {str(e)}") from e
        return False
    
    async def count(self) -> int:
        """
        Compte le nombre total d'instances dans la table.
        
        Returns:
            Nombre total d'enregistrements
            
        Example:
            >>> total = await repository.count()
            >>> print(f"Nombre total de publications: {total}")
        """
        stmt = select(func.count()).select_from(self.model)
        result = await self.db.execute(stmt)
        return result.scalar_one()
