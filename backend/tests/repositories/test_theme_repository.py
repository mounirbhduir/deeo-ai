"""
Tests unitaires pour ThemeRepository

Teste les méthodes spécialisées : hiérarchie, recherche, thèmes les plus utilisés.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ThemeRepository


@pytest.mark.asyncio
async def test_get_by_nom_existing(
    async_session: AsyncSession,
    theme_data: dict
):
    """Test récupération par label exact."""
    # Arrange
    repository = ThemeRepository(async_session)
    created = await repository.create(theme_data)
    
    # Act
    result = await repository.get_by_nom(theme_data["label"])
    
    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.label == theme_data["label"]


@pytest.mark.asyncio
async def test_get_by_nom_nonexistent(async_session: AsyncSession):
    """Test récupération par label inexistant."""
    # Arrange
    repository = ThemeRepository(async_session)
    
    # Act
    result = await repository.get_by_nom("Nonexistent Theme")
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_search(
    async_session: AsyncSession,
    theme_data: dict
):
    """Test recherche fuzzy sur label et description."""
    # Arrange
    repository = ThemeRepository(async_session)
    await repository.create(theme_data)
    
    # Act
    results_by_label = await repository.search("Learning")
    results_by_description = await repository.search("algorithmes")
    
    # Assert
    assert len(results_by_label) >= 1
    assert len(results_by_description) >= 1


@pytest.mark.asyncio
async def test_get_most_used(
    async_session: AsyncSession,
    theme_data: dict
):
    """Test récupération des thèmes les plus utilisés."""
    # Arrange
    repository = ThemeRepository(async_session)
    
    # Créer thèmes avec différents nombres de publications
    pub_counts = [100, 500, 1000, 50, 750]
    
    for i, count in enumerate(pub_counts):
        data = theme_data.copy()
        data["label"] = f"Theme {i}"
        data["nombre_publications"] = count
        await repository.create(data)
    
    # Act
    top_3 = await repository.get_most_used(limit=3)
    
    # Assert
    assert len(top_3) == 3
    theme1, count1 = top_3[0]
    theme2, count2 = top_3[1]
    theme3, count3 = top_3[2]
    
    assert count1 == 1000
    assert count2 == 750
    assert count3 == 500


@pytest.mark.asyncio
async def test_get_by_level(
    async_session: AsyncSession,
    theme_data: dict
):
    """Test récupération par niveau hiérarchique."""
    # Arrange
    repository = ThemeRepository(async_session)
    
    # Créer thèmes de différents niveaux
    levels = [0, 1, 1, 2, 2, 2]
    
    for i, level in enumerate(levels):
        data = theme_data.copy()
        data["label"] = f"Theme Level {level} #{i}"
        data["niveau_hierarchie"] = level
        await repository.create(data)
    
    # Act
    level_0 = await repository.get_by_level(0)
    level_1 = await repository.get_by_level(1)
    level_2 = await repository.get_by_level(2)
    
    # Assert
    assert len(level_0) == 1
    assert len(level_1) == 2
    assert len(level_2) == 3


@pytest.mark.asyncio
async def test_get_children(
    async_session: AsyncSession,
    theme_data: dict
):
    """Test récupération des thèmes enfants."""
    # Arrange
    repository = ThemeRepository(async_session)
    
    # Créer thème parent
    parent_data = theme_data.copy()
    parent_data["label"] = "Parent Theme"
    parent_data["niveau_hierarchie"] = 1
    parent = await repository.create(parent_data)
    
    # Créer 3 thèmes enfants
    for i in range(3):
        child_data = theme_data.copy()
        child_data["label"] = f"Child Theme {i}"
        child_data["niveau_hierarchie"] = 2
        child_data["parent_id"] = parent.id
        await repository.create(child_data)
    
    # Act
    children = await repository.get_children(parent.id)
    
    # Assert
    assert len(children) == 3
    assert all(child.parent_id == parent.id for child in children)


@pytest.mark.asyncio
async def test_get_root_themes(
    async_session: AsyncSession,
    theme_data: dict
):
    """Test récupération des thèmes racine."""
    # Arrange
    repository = ThemeRepository(async_session)
    
    # Créer thème parent (racine)
    parent_data = theme_data.copy()
    parent_data["label"] = "Root Theme"
    parent_data["parent_id"] = None
    parent = await repository.create(parent_data)
    
    # Créer thème enfant (non racine)
    child_data = theme_data.copy()
    child_data["label"] = "Child Theme"
    child_data["parent_id"] = parent.id
    await repository.create(child_data)
    
    # Act
    roots = await repository.get_root_themes()
    
    # Assert
    assert len(roots) == 1
    assert roots[0].parent_id is None


@pytest.mark.asyncio
async def test_get_with_hierarchy(
    async_session: AsyncSession,
    theme_data: dict
):
    """Test eager loading de la hiérarchie (parent + enfants)."""
    # Arrange
    repository = ThemeRepository(async_session)
    
    # Créer thème parent
    parent_data = theme_data.copy()
    parent_data["label"] = "Parent"
    parent_data["parent_id"] = None
    parent = await repository.create(parent_data)
    
    # Créer thème du milieu
    middle_data = theme_data.copy()
    middle_data["label"] = "Middle"
    middle_data["parent_id"] = parent.id
    middle = await repository.create(middle_data)
    
    # Créer thème enfant
    child_data = theme_data.copy()
    child_data["label"] = "Child"
    child_data["parent_id"] = middle.id
    await repository.create(child_data)
    
    # Act
    result = await repository.get_with_hierarchy(middle.id)
    
    # Assert
    assert result is not None
    assert result.id == middle.id
    assert hasattr(result, 'parent')
    assert hasattr(result, 'enfants')


@pytest.mark.asyncio
async def test_count_by_level(
    async_session: AsyncSession,
    theme_data: dict
):
    """Test comptage par niveau hiérarchique."""
    # Arrange
    repository = ThemeRepository(async_session)
    
    # Créer thèmes de différents niveaux
    for i in range(3):
        data = theme_data.copy()
        data["label"] = f"Level 1 Theme {i}"
        data["niveau_hierarchie"] = 1
        await repository.create(data)
    
    for i in range(5):
        data = theme_data.copy()
        data["label"] = f"Level 2 Theme {i}"
        data["niveau_hierarchie"] = 2
        await repository.create(data)
    
    # Act
    count_1 = await repository.count_by_level(1)
    count_2 = await repository.count_by_level(2)
    count_3 = await repository.count_by_level(3)
    
    # Assert
    assert count_1 == 3
    assert count_2 == 5
    assert count_3 == 0


@pytest.mark.asyncio
async def test_search_by_path(
    async_session: AsyncSession,
    theme_data: dict
):
    """Test recherche par fragment de chemin hiérarchique."""
    # Arrange
    repository = ThemeRepository(async_session)
    
    # Créer thèmes avec différents chemins
    paths = [
        "AI/Machine Learning",
        "AI/Machine Learning/Deep Learning",
        "AI/Computer Vision",
    ]
    
    for i, path in enumerate(paths):
        data = theme_data.copy()
        data["label"] = f"Theme {i}"
        data["chemin_hierarchie"] = path
        await repository.create(data)
    
    # Act
    ml_themes = await repository.search_by_path("Machine Learning")
    cv_themes = await repository.search_by_path("Computer Vision")
    
    # Assert
    assert len(ml_themes) == 2  # ML et Deep Learning
    assert len(cv_themes) == 1


@pytest.mark.asyncio
async def test_get_with_publications(
    async_session: AsyncSession,
    created_theme
):
    """Test eager loading des publications."""
    # Arrange
    repository = ThemeRepository(async_session)
    
    # Act
    result = await repository.get_with_publications(created_theme.id)
    
    # Assert
    assert result is not None
    assert result.id == created_theme.id
    assert hasattr(result, 'publications')
