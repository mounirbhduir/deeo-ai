"""Base service with generic CRUD orchestration."""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.repositories.base_repository import BaseRepository


ModelType = TypeVar("ModelType")
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[ModelType, RepositoryType]):
    """
    Base service providing generic CRUD operations with business logic.
    
    This service orchestrates repositories and adds validation, business rules,
    and transaction management.
    
    Attributes:
        repository: The repository instance for data access
        db: AsyncSession for database operations
    
    Type Parameters:
        ModelType: The SQLAlchemy model type
        RepositoryType: The repository type
    """
    
    def __init__(self, repository: RepositoryType, db: AsyncSession):
        """
        Initialize the base service.
        
        Args:
            repository: Repository instance for data access
            db: AsyncSession for database operations
        """
        self.repository = repository
        self.db = db
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new entity with validation.
        
        Args:
            obj_in: Dictionary with entity data
            
        Returns:
            Created entity
            
        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraints are violated
        """
        # Pre-creation validation
        await self._validate_create(obj_in)
        
        try:
            # Create via repository
            entity = await self.repository.create(obj_in)
            return entity
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Integrity error during creation: {str(e)}")
    
    async def get(self, entity_id: UUID) -> Optional[ModelType]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity UUID

        Returns:
            Entity if found, None otherwise
        """
        return await self.repository.get(entity_id)
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple entities with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of entities
        """
        return await self.repository.get_multi(skip=skip, limit=limit)
    
    async def update(
        self,
        entity_id: UUID,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update an entity with validation.

        Args:
            entity_id: Entity UUID
            obj_in: Dictionary with updated data

        Returns:
            Updated entity if found, None otherwise

        Raises:
            ValueError: If validation fails
            IntegrityError: If database constraints are violated
        """
        # Pre-update validation
        await self._validate_update(entity_id, obj_in)

        try:
            # Update via repository
            entity = await self.repository.update(entity_id, obj_in)
            return entity
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Integrity error during update: {str(e)}")
    
    async def delete(self, entity_id: UUID) -> bool:
        """
        Soft delete an entity.

        Args:
            entity_id: Entity UUID

        Returns:
            True if deleted, False otherwise
        """
        return await self.repository.delete(entity_id)
    
    async def count(self) -> int:
        """
        Count total entities (excluding soft-deleted).
        
        Returns:
            Total count
        """
        return await self.repository.count()
    
    async def _validate_create(self, obj_in: Dict[str, Any]) -> None:
        """
        Validate data before creation.
        
        Override this method in subclasses to add specific validation logic.
        
        Args:
            obj_in: Data to validate
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    async def _validate_update(
        self,
        entity_id: UUID,
        obj_in: Dict[str, Any]
    ) -> None:
        """
        Validate data before update.

        Override this method in subclasses to add specific validation logic.

        Args:
            entity_id: Entity UUID being updated
            obj_in: Data to validate

        Raises:
            ValueError: If validation fails
        """
        pass
