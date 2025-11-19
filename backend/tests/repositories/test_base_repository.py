"""
Tests unitaires pour BaseRepository

Teste les opérations CRUD de base héritées par tous les repositories.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import PublicationRepository


@pytest.mark.asyncio
async def test_create_success(async_session: AsyncSession, publication_data: dict):
    """Test création d'une nouvelle publication."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Act
    result = await repository.create(publication_data)
    
    # Assert
    assert result.id is not None
    assert result.titre == publication_data["titre"]
    assert result.doi == publication_data["doi"]
    assert result.arxiv_id == publication_data["arxiv_id"]


@pytest.mark.asyncio
async def test_create_with_integrity_error(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test création avec violation de contrainte d'intégrité (DOI dupliqué)."""
    # Arrange
    repository = PublicationRepository(async_session)
    await repository.create(publication_data)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Integrity constraint violated"):
        await repository.create(publication_data)  # Même DOI


@pytest.mark.asyncio
async def test_get_existing(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test récupération d'une publication existante par ID."""
    # Arrange
    repository = PublicationRepository(async_session)
    created = await repository.create(publication_data)
    
    # Act
    result = await repository.get(created.id)
    
    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.titre == publication_data["titre"]


@pytest.mark.asyncio
async def test_get_nonexistent(async_session: AsyncSession):
    """Test récupération d'une publication inexistante."""
    # Arrange
    from uuid import uuid4
    repository = PublicationRepository(async_session)
    fake_id = uuid4()
    
    # Act
    result = await repository.get(fake_id)
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_multi_with_pagination(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test récupération multiple avec pagination."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Créer 5 publications
    for i in range(5):
        data = publication_data.copy()
        data["titre"] = f"Publication {i}"
        data["doi"] = f"10.1234/test.{i}"
        data["arxiv_id"] = f"2401.{10000+i:05d}"  # Valid arXiv format: YYMM.NNNNN
        await repository.create(data)
    
    # Act - Page 1 (2 premiers)
    page1 = await repository.get_multi(skip=0, limit=2)
    
    # Act - Page 2 (2 suivants)
    page2 = await repository.get_multi(skip=2, limit=2)
    
    # Assert
    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id  # Différentes publications


@pytest.mark.asyncio
async def test_get_multi_empty(async_session: AsyncSession):
    """Test récupération multiple sur table vide."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Act
    results = await repository.get_multi()
    
    # Assert
    assert results == []


@pytest.mark.asyncio
async def test_update_success(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test mise à jour d'une publication existante."""
    # Arrange
    repository = PublicationRepository(async_session)
    created = await repository.create(publication_data)
    
    updates = {
        "titre": "Updated Title",
        "nombre_citations": 999
    }
    
    # Act
    updated = await repository.update(created.id, updates)
    
    # Assert
    assert updated is not None
    assert updated.id == created.id
    assert updated.titre == "Updated Title"
    assert updated.nombre_citations == 999


@pytest.mark.asyncio
async def test_update_nonexistent(async_session: AsyncSession):
    """Test mise à jour d'une publication inexistante."""
    # Arrange
    from uuid import uuid4
    repository = PublicationRepository(async_session)
    fake_id = uuid4()
    
    updates = {"titre": "New Title"}
    
    # Act
    result = await repository.update(fake_id, updates)
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_delete_success(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test suppression d'une publication existante."""
    # Arrange
    repository = PublicationRepository(async_session)
    created = await repository.create(publication_data)
    
    # Act
    deleted = await repository.delete(created.id)
    
    # Assert
    assert deleted is True
    
    # Vérifier que la publication n'existe plus
    result = await repository.get(created.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_nonexistent(async_session: AsyncSession):
    """Test suppression d'une publication inexistante."""
    # Arrange
    from uuid import uuid4
    repository = PublicationRepository(async_session)
    fake_id = uuid4()
    
    # Act
    deleted = await repository.delete(fake_id)
    
    # Assert
    assert deleted is False


@pytest.mark.asyncio
async def test_count(async_session: AsyncSession, publication_data: dict):
    """Test comptage total des publications."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Créer 3 publications
    for i in range(3):
        data = publication_data.copy()
        data["doi"] = f"10.1234/test.{i}"
        data["arxiv_id"] = f"2401.{10000+i:05d}"  # Valid arXiv format: YYMM.NNNNN
        await repository.create(data)
    
    # Act
    count = await repository.count()
    
    # Assert
    assert count == 3


@pytest.mark.asyncio
async def test_count_empty(async_session: AsyncSession):
    """Test comptage sur table vide."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Act
    count = await repository.count()
    
    # Assert
    assert count == 0
