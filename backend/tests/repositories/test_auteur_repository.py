"""
Tests unitaires pour AuteurRepository

Teste les méthodes spécialisées : ORCID, Semantic Scholar ID, recherche par nom, h-index.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import AuteurRepository


@pytest.mark.asyncio
async def test_get_by_orcid_existing(
    async_session: AsyncSession,
    auteur_data: dict
):
    """Test récupération par ORCID existant."""
    # Arrange
    repository = AuteurRepository(async_session)
    created = await repository.create(auteur_data)
    
    # Act
    result = await repository.get_by_orcid(auteur_data["orcid"])
    
    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.orcid == auteur_data["orcid"]


@pytest.mark.asyncio
async def test_get_by_orcid_nonexistent(async_session: AsyncSession):
    """Test récupération par ORCID inexistant."""
    # Arrange
    repository = AuteurRepository(async_session)
    
    # Act
    result = await repository.get_by_orcid("0000-0000-0000-0000")
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_by_semantic_scholar_id_existing(
    async_session: AsyncSession,
    auteur_data: dict
):
    """Test récupération par Semantic Scholar ID existant."""
    # Arrange
    repository = AuteurRepository(async_session)
    created = await repository.create(auteur_data)
    
    # Act
    result = await repository.get_by_semantic_scholar_id(
        auteur_data["semantic_scholar_id"]
    )
    
    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.semantic_scholar_id == auteur_data["semantic_scholar_id"]


@pytest.mark.asyncio
async def test_get_by_semantic_scholar_id_nonexistent(async_session: AsyncSession):
    """Test récupération par Semantic Scholar ID inexistant."""
    # Arrange
    repository = AuteurRepository(async_session)
    
    # Act
    result = await repository.get_by_semantic_scholar_id("nonexistent_id")
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_search_by_name_nom(
    async_session: AsyncSession,
    auteur_data: dict
):
    """Test recherche par nom de famille."""
    # Arrange
    repository = AuteurRepository(async_session)
    await repository.create(auteur_data)
    
    # Act
    results = await repository.search_by_name("Vaswani")
    
    # Assert
    assert len(results) == 1
    assert results[0].nom == "Vaswani"


@pytest.mark.asyncio
async def test_search_by_name_prenom(
    async_session: AsyncSession,
    auteur_data: dict
):
    """Test recherche par prénom."""
    # Arrange
    repository = AuteurRepository(async_session)
    await repository.create(auteur_data)
    
    # Act
    results = await repository.search_by_name("Ashish")
    
    # Assert
    assert len(results) == 1
    assert results[0].prenom == "Ashish"


@pytest.mark.asyncio
async def test_search_by_name_partial(
    async_session: AsyncSession,
    auteur_data: dict
):
    """Test recherche avec terme partiel."""
    # Arrange
    repository = AuteurRepository(async_session)
    await repository.create(auteur_data)
    
    # Act
    results = await repository.search_by_name("Vas")
    
    # Assert
    assert len(results) == 1
    assert "Vas" in results[0].nom


@pytest.mark.asyncio
async def test_search_by_name_no_results(async_session: AsyncSession):
    """Test recherche sans résultats."""
    # Arrange
    repository = AuteurRepository(async_session)
    
    # Act
    results = await repository.search_by_name("Nonexistent")
    
    # Assert
    assert results == []


@pytest.mark.asyncio
async def test_get_by_h_index_range(
    async_session: AsyncSession,
    auteur_data: dict
):
    """Test récupération par plage de h-index."""
    # Arrange
    repository = AuteurRepository(async_session)
    
    # Créer auteurs avec différents h-index
    h_indices = [10, 25, 50, 75, 100]
    
    for i, h_index in enumerate(h_indices):
        data = auteur_data.copy()
        data["nom"] = f"Auteur{i}"
        data["orcid"] = f"0000-0002-{i:04d}-{i:04d}"
        data["semantic_scholar_id"] = f"ss_{i}"
        data["h_index"] = h_index
        await repository.create(data)
    
    # Act
    range_20_60 = await repository.get_by_h_index_range(min_h=20, max_h=60)
    range_70_200 = await repository.get_by_h_index_range(min_h=70, max_h=200)
    
    # Assert
    assert len(range_20_60) == 2  # 25 et 50
    assert all(20 <= a.h_index <= 60 for a in range_20_60)
    
    assert len(range_70_200) == 2  # 75 et 100
    assert all(70 <= a.h_index <= 200 for a in range_70_200)
    
    # Vérifier tri décroissant
    assert range_20_60[0].h_index >= range_20_60[1].h_index
    assert range_70_200[0].h_index >= range_70_200[1].h_index


@pytest.mark.asyncio
async def test_get_top_by_h_index(
    async_session: AsyncSession,
    auteur_data: dict
):
    """Test récupération des top auteurs par h-index."""
    # Arrange
    repository = AuteurRepository(async_session)
    
    # Créer auteurs avec différents h-index
    h_indices = [100, 75, 50, 25, 10]
    
    for i, h_index in enumerate(h_indices):
        data = auteur_data.copy()
        data["nom"] = f"Auteur{i}"
        data["orcid"] = f"0000-0002-{i:04d}-{i:04d}"
        data["semantic_scholar_id"] = f"ss_{i}"
        data["h_index"] = h_index
        await repository.create(data)
    
    # Act
    top_3 = await repository.get_top_by_h_index(limit=3)
    
    # Assert
    assert len(top_3) == 3
    assert top_3[0].h_index == 100
    assert top_3[1].h_index == 75
    assert top_3[2].h_index == 50


@pytest.mark.asyncio
async def test_count_by_h_index_threshold(
    async_session: AsyncSession,
    auteur_data: dict
):
    """Test comptage des auteurs au-dessus d'un seuil de h-index."""
    # Arrange
    repository = AuteurRepository(async_session)
    
    # Créer auteurs avec différents h-index
    h_indices = [10, 25, 50, 75, 100]
    
    for i, h_index in enumerate(h_indices):
        data = auteur_data.copy()
        data["nom"] = f"Auteur{i}"
        data["orcid"] = f"0000-0002-{i:04d}-{i:04d}"
        data["semantic_scholar_id"] = f"ss_{i}"
        data["h_index"] = h_index
        await repository.create(data)
    
    # Act
    count_50_plus = await repository.count_by_h_index_threshold(50)
    count_80_plus = await repository.count_by_h_index_threshold(80)
    
    # Assert
    assert count_50_plus == 3  # 50, 75, 100
    assert count_80_plus == 1  # 100


@pytest.mark.asyncio
async def test_get_with_publications(
    async_session: AsyncSession,
    created_auteur
):
    """Test eager loading des publications."""
    # Arrange
    repository = AuteurRepository(async_session)
    
    # Act
    result = await repository.get_with_publications(created_auteur.id)
    
    # Assert
    assert result is not None
    assert result.id == created_auteur.id
    assert hasattr(result, 'publications')


@pytest.mark.asyncio
async def test_get_with_affiliations(
    async_session: AsyncSession,
    created_auteur
):
    """Test eager loading des affiliations."""
    # Arrange
    repository = AuteurRepository(async_session)
    
    # Act
    result = await repository.get_with_affiliations(created_auteur.id)
    
    # Assert
    assert result is not None
    assert result.id == created_auteur.id
    assert hasattr(result, 'affiliations')
