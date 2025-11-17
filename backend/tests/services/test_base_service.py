"""Tests for BaseService."""

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import IntegrityError

from app.services.base_service import BaseService
from app.repositories.base_repository import BaseRepository


class MockModel:
    """Mock model for testing."""
    def __init__(self, id=None, **kwargs):
        self.id = id
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockRepository(BaseRepository):
    """Mock repository for testing."""
    def __init__(self, db):
        super().__init__(MockModel, db)


class TestBaseService:
    """Test cases for BaseService."""
    
    @pytest.mark.asyncio
    async def test_create_success(self, mock_db_session):
        """Test successful entity creation."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        mock_entity = MockModel(id=1, name="Test")
        repository.create = AsyncMock(return_value=mock_entity)
        
        data = {"name": "Test"}
        
        # Act
        result = await service.create(data)
        
        # Assert
        assert result.id == 1
        assert result.name == "Test"
        repository.create.assert_called_once_with(data)
    
    @pytest.mark.asyncio
    async def test_create_integrity_error(self, mock_db_session):
        """Test creation with integrity error."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        repository.create = AsyncMock(side_effect=IntegrityError("", "", ""))
        
        data = {"name": "Test"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Integrity error"):
            await service.create(data)
        
        mock_db_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_success(self, mock_db_session):
        """Test successful entity retrieval by ID."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        mock_entity = MockModel(id=1, name="Test")
        repository.get = AsyncMock(return_value=mock_entity)
        
        # Act
        result = await service.get(1)
        
        # Assert
        assert result.id == 1
        repository.get.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_db_session):
        """Test entity retrieval when not found."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        repository.get = AsyncMock(return_value=None)
        
        # Act
        result = await service.get(999)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_multi(self, mock_db_session):
        """Test retrieving multiple entities."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        mock_entities = [
            MockModel(id=1, name="Test1"),
            MockModel(id=2, name="Test2")
        ]
        repository.get_multi = AsyncMock(return_value=mock_entities)
        
        # Act
        result = await service.get_multi(skip=0, limit=10)
        
        # Assert
        assert len(result) == 2
        repository.get_multi.assert_called_once_with(skip=0, limit=10)
    
    @pytest.mark.asyncio
    async def test_update_success(self, mock_db_session):
        """Test successful entity update."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        updated_entity = MockModel(id=1, name="Updated")
        repository.update = AsyncMock(return_value=updated_entity)
        
        data = {"name": "Updated"}
        
        # Act
        result = await service.update(1, data)
        
        # Assert
        assert result.name == "Updated"
        repository.update.assert_called_once_with(1, data)
    
    @pytest.mark.asyncio
    async def test_update_integrity_error(self, mock_db_session):
        """Test update with integrity error."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        repository.update = AsyncMock(side_effect=IntegrityError("", "", ""))
        
        data = {"name": "Updated"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Integrity error"):
            await service.update(1, data)
        
        mock_db_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_success(self, mock_db_session):
        """Test successful entity deletion."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        repository.delete = AsyncMock(return_value=True)
        
        # Act
        result = await service.delete(1)
        
        # Assert
        assert result is True
        repository.delete.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_db_session):
        """Test deletion when entity not found."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        repository.delete = AsyncMock(return_value=False)
        
        # Act
        result = await service.delete(999)
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_count(self, mock_db_session):
        """Test entity counting."""
        # Arrange
        repository = MockRepository(mock_db_session)
        service = BaseService(repository, mock_db_session)
        
        repository.count = AsyncMock(return_value=42)
        
        # Act
        result = await service.count()
        
        # Assert
        assert result == 42
        repository.count.assert_called_once()
