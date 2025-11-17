"""Tests for AuteurService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.auteur_service import AuteurService


class TestAuteurService:
    """Test cases for AuteurService."""
    
    @pytest.mark.asyncio
    async def test_create_with_affiliations(
        self,
        mock_db_session,
        sample_auteur_data,
        sample_auteur
    ):
        """Test creating author with affiliations."""
        # Arrange
        service = AuteurService(mock_db_session)
        service.create = AsyncMock(return_value=sample_auteur)
        
        affiliations = [
            {
                "organisation_id": 1,
                "date_debut": "2020-01-01",
                "date_fin": None,
                "poste": "Professor"
            }
        ]
        
        # Act
        result = await service.create_with_affiliations(
            sample_auteur_data,
            affiliations
        )
        
        # Assert
        assert result is not None
        service.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_h_index_success(
        self,
        mock_db_session,
        sample_auteur
    ):
        """Test updating author h-index."""
        # Arrange
        service = AuteurService(mock_db_session)
        service.update = AsyncMock(return_value=sample_auteur)
        
        # Act
        result = await service.update_h_index(1, 30)
        
        # Assert
        service.update.assert_called_once_with(1, {"h_index": 30})
    
    @pytest.mark.asyncio
    async def test_update_h_index_negative_fails(
        self,
        mock_db_session
    ):
        """Test updating with negative h-index fails."""
        # Arrange
        service = AuteurService(mock_db_session)
        
        # Act & Assert
        with pytest.raises(ValueError, match="h-index cannot be negative"):
            await service.update_h_index(1, -5)
    
    @pytest.mark.asyncio
    async def test_get_top_contributors(
        self,
        mock_db_session,
        sample_auteur
    ):
        """Test getting top contributors."""
        # Arrange
        service = AuteurService(mock_db_session)

        # Mock execute result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_auteur]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await service.get_top_contributors(limit=10, min_h_index=20)

        # Assert
        assert len(result) == 1
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_by_orcid(
        self,
        mock_db_session,
        sample_auteur
    ):
        """Test searching by ORCID."""
        # Arrange
        service = AuteurService(mock_db_session)
        service.repository.get_by_orcid = AsyncMock(return_value=sample_auteur)
        
        # Act
        result = await service.search_by_name_or_orcid("0000-0001-2345-6789")
        
        # Assert
        assert len(result) == 1
        assert result[0].orcid == "0000-0001-2345-6789"
    
    @pytest.mark.asyncio
    async def test_search_by_name(
        self,
        mock_db_session,
        sample_auteur
    ):
        """Test searching by name."""
        # Arrange
        service = AuteurService(mock_db_session)
        service.repository.search_by_name = AsyncMock(return_value=[sample_auteur])
        
        # Act
        result = await service.search_by_name_or_orcid("Doe")
        
        # Assert
        assert len(result) == 1
        service.repository.search_by_name.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_create_invalid_orcid_format_fails(
        self,
        mock_db_session
    ):
        """Test validation fails with invalid ORCID format."""
        # Arrange
        service = AuteurService(mock_db_session)
        
        invalid_data = {"orcid": "invalid-orcid"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid ORCID format"):
            await service._validate_create(invalid_data)
    
    @pytest.mark.asyncio
    async def test_validate_create_duplicate_orcid_fails(
        self,
        mock_db_session,
        sample_auteur
    ):
        """Test validation fails with duplicate ORCID."""
        # Arrange
        service = AuteurService(mock_db_session)
        service.repository.get_by_orcid = AsyncMock(return_value=sample_auteur)
        
        data = {"orcid": "0000-0001-2345-6789"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            await service._validate_create(data)
    
    @pytest.mark.asyncio
    async def test_validate_update_negative_h_index_fails(
        self,
        mock_db_session
    ):
        """Test validation fails with negative h-index."""
        # Arrange
        service = AuteurService(mock_db_session)
        service.repository.get_by_orcid = AsyncMock(return_value=None)
        
        data = {"h_index": -10}
        
        # Act & Assert
        with pytest.raises(ValueError, match="h-index cannot be negative"):
            await service._validate_update(1, data)
