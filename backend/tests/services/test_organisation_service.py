"""Tests for OrganisationService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.organisation_service import OrganisationService


class TestOrganisationService:
    """Test cases for OrganisationService."""
    
    @pytest.mark.asyncio
    async def test_search_organizations(
        self,
        mock_db_session,
        sample_organisation
    ):
        """Test searching organizations by name."""
        # Arrange
        service = OrganisationService(mock_db_session)
        service.repository.search = AsyncMock(return_value=[sample_organisation])
        
        # Act
        result = await service.search_organizations("University", skip=0, limit=10)
        
        # Assert
        assert len(result) == 1
        service.repository.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_country(
        self,
        mock_db_session,
        sample_organisation
    ):
        """Test getting organizations by country."""
        # Arrange
        service = OrganisationService(mock_db_session)
        service.repository.get_by_country = AsyncMock(return_value=[sample_organisation])
        
        # Act
        result = await service.get_by_country(1, skip=0, limit=50)
        
        # Assert
        assert len(result) == 1
        service.repository.get_by_country.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_top_by_publications(
        self,
        mock_db_session,
        sample_organisation
    ):
        """Test getting top organizations by publications."""
        # Arrange
        service = OrganisationService(mock_db_session)

        # Mock execute result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_organisation]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await service.get_top_by_publications(limit=10, min_publications=50)

        # Assert
        assert len(result) == 1
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_top_by_ranking(
        self,
        mock_db_session,
        sample_organisation
    ):
        """Test getting top organizations by world ranking."""
        # Arrange
        service = OrganisationService(mock_db_session)

        # Mock execute result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_organisation]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await service.get_top_by_ranking(limit=100)

        # Assert
        assert len(result) == 1
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_create_duplicate_name_fails(
        self,
        mock_db_session,
        sample_organisation
    ):
        """Test validation fails with duplicate organization name."""
        # Arrange
        service = OrganisationService(mock_db_session)
        service.repository.get_by_nom = AsyncMock(return_value=sample_organisation)
        
        data = {"nom": "Test University"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            await service._validate_create(data)
    
    @pytest.mark.asyncio
    async def test_validate_create_invalid_type_fails(
        self,
        mock_db_session
    ):
        """Test validation fails with invalid organization type."""
        # Arrange
        service = OrganisationService(mock_db_session)
        service.repository.get_by_nom = AsyncMock(return_value=None)
        
        data = {"nom": "Test Org", "type_organisation": "invalid_type"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid organization type"):
            await service._validate_create(data)
    
    @pytest.mark.asyncio
    async def test_validate_update_duplicate_name_fails(
        self,
        mock_db_session,
        sample_organisation
    ):
        """Test validation fails when updating to duplicate name."""
        # Arrange
        service = OrganisationService(mock_db_session)
        
        # Mock get_by_nom to return different organization
        other_org = sample_organisation
        other_org.id = 2
        service.repository.get_by_nom = AsyncMock(return_value=other_org)
        
        data = {"nom": "Test University"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            await service._validate_update(1, data)
