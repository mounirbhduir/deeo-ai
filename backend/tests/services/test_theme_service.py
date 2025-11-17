"""Tests for ThemeService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.theme_service import ThemeService
from app.models.theme import Theme


class TestThemeService:
    """Test cases for ThemeService."""
    
    @pytest.mark.asyncio
    async def test_get_root_themes(
        self,
        mock_db_session,
        sample_theme
    ):
        """Test getting root themes."""
        # Arrange
        service = ThemeService(mock_db_session)
        service.repository.get_root_themes = AsyncMock(return_value=[sample_theme])
        
        # Act
        result = await service.get_root_themes()
        
        # Assert
        assert len(result) == 1
        service.repository.get_root_themes.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_children(
        self,
        mock_db_session,
        sample_theme
    ):
        """Test getting theme children."""
        # Arrange
        service = ThemeService(mock_db_session)
        
        # Create a separate child theme instance
        child_theme = Theme(
            label="Deep Learning",
            description="Subfield of ML",
            niveau_hierarchie=2,
            parent_id=1,
            nombre_publications=100
        )
        child_theme.id = 2
        
        service.repository.get_children = AsyncMock(return_value=[child_theme])
        
        # Act
        result = await service.get_children(1)
        
        # Assert
        assert len(result) == 1
        service.repository.get_children.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_get_by_level(
        self,
        mock_db_session,
        sample_theme
    ):
        """Test getting themes by hierarchical level."""
        # Arrange
        service = ThemeService(mock_db_session)
        service.repository.get_by_level = AsyncMock(return_value=[sample_theme])
        
        # Act
        result = await service.get_by_level(1, skip=0, limit=20)
        
        # Assert
        assert len(result) == 1
        service.repository.get_by_level.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_popular_themes(
        self,
        mock_db_session,
        sample_theme
    ):
        """Test getting popular themes by publication count."""
        # Arrange
        service = ThemeService(mock_db_session)

        # Mock execute result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_theme]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await service.get_popular_themes(limit=10, min_publications=50)

        # Assert
        assert len(result) == 1
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_theme_hierarchy(
        self,
        mock_db_session
    ):
        """Test getting theme hierarchy path."""
        # Arrange
        service = ThemeService(mock_db_session)
        
        # IMPORTANT: Create TWO SEPARATE theme instances
        # Not two references to the same object!
        
        # Root theme (parent)
        parent_theme = Theme(
            label="Artificial Intelligence",
            description="Root AI theme",
            niveau_hierarchie=0,
            parent_id=None,
            nombre_publications=500
        )
        parent_theme.id = 2
        
        # Child theme
        child_theme = Theme(
            label="Machine Learning",
            description="ML subfield",
            niveau_hierarchie=1,
            parent_id=2,  # Points to parent
            nombre_publications=200
        )
        child_theme.id = 1
        
        # Mock get calls to return different objects
        async def mock_get(theme_id):
            if theme_id == 1:
                return child_theme
            elif theme_id == 2:
                return parent_theme
            return None
        
        service.get = AsyncMock(side_effect=mock_get)
        
        # Act
        result = await service.get_theme_hierarchy(1)
        
        # Assert
        assert len(result) == 2
        assert result[0].id == 2  # Parent first
        assert result[1].id == 1  # Child second
    
    @pytest.mark.asyncio
    async def test_search_themes(
        self,
        mock_db_session,
        sample_theme
    ):
        """Test searching themes by label."""
        # Arrange
        service = ThemeService(mock_db_session)

        # Mock execute result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_theme]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await service.search_themes("Machine", skip=0, limit=10)

        # Assert
        assert len(result) == 1
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_create_invalid_level_fails(
        self,
        mock_db_session
    ):
        """Test validation fails with invalid hierarchical level."""
        # Arrange
        service = ThemeService(mock_db_session)
        
        data = {"niveau_hierarchie": 15}  # > 10
        
        # Act & Assert
        with pytest.raises(ValueError, match="between 0 and 10"):
            await service._validate_create(data)
    
    @pytest.mark.asyncio
    async def test_validate_create_parent_not_found_fails(
        self,
        mock_db_session
    ):
        """Test validation fails when parent doesn't exist."""
        # Arrange
        service = ThemeService(mock_db_session)
        service.get = AsyncMock(return_value=None)
        
        data = {"parent_id": 999, "niveau_hierarchie": 1}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Parent theme.*not found"):
            await service._validate_create(data)
    
    @pytest.mark.asyncio
    async def test_validate_create_wrong_child_level_fails(
        self,
        mock_db_session
    ):
        """Test validation fails when child level doesn't match parent + 1."""
        # Arrange
        service = ThemeService(mock_db_session)
        
        # Create parent theme
        parent = Theme(
            label="AI",
            description="Parent",
            niveau_hierarchie=1,
            parent_id=None,
            nombre_publications=100
        )
        parent.id = 1
        
        service.get = AsyncMock(return_value=parent)
        
        data = {"parent_id": 1, "niveau_hierarchie": 5}  # Should be 2
        
        # Act & Assert
        with pytest.raises(ValueError, match="Child theme level must be"):
            await service._validate_create(data)
    
    @pytest.mark.asyncio
    async def test_validate_update_self_parent_fails(
        self,
        mock_db_session
    ):
        """Test validation fails when theme tries to be its own parent."""
        # Arrange
        service = ThemeService(mock_db_session)
        service.get = AsyncMock(return_value=None)
        
        data = {"parent_id": 1}
        
        # Act & Assert
        with pytest.raises(ValueError, match="cannot be its own parent"):
            await service._validate_update(1, data)
