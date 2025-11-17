"""Tests for PublicationService."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from app.services.publication_service import PublicationService


class TestPublicationService:
    """Test cases for PublicationService."""
    
    @pytest.mark.asyncio
    async def test_create_with_authors(
        self,
        mock_db_session,
        sample_publication_data
    ):
        """Test creating publication with authors."""
        # Arrange
        service = PublicationService(mock_db_session)
        service.create = AsyncMock(return_value=sample_publication_data)
        
        author_ids = [1, 2, 3]
        ordre = [1, 2, 3]
        
        # Act
        result = await service.create_with_authors(
            sample_publication_data,
            author_ids,
            ordre
        )
        
        # Assert
        assert result is not None
        service.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_with_authors_no_authors_fails(
        self,
        mock_db_session,
        sample_publication_data
    ):
        """Test creating publication without authors fails."""
        # Arrange
        service = PublicationService(mock_db_session)
        
        # Act & Assert
        with pytest.raises(ValueError, match="At least one author is required"):
            await service.create_with_authors(sample_publication_data, [], None)
    
    @pytest.mark.asyncio
    async def test_create_with_authors_ordre_mismatch_fails(
        self,
        mock_db_session,
        sample_publication_data
    ):
        """Test creating publication with mismatched ordre length fails."""
        # Arrange
        service = PublicationService(mock_db_session)
        service.create = AsyncMock(return_value=sample_publication_data)
        
        author_ids = [1, 2]
        ordre = [1]  # Mismatch
        
        # Act & Assert
        with pytest.raises(ValueError, match="ordre list must match"):
            await service.create_with_authors(
                sample_publication_data,
                author_ids,
                ordre
            )
    
    @pytest.mark.asyncio
    async def test_update_status_success(
        self,
        mock_db_session,
        sample_publication
    ):
        """Test updating publication status."""
        # Arrange
        service = PublicationService(mock_db_session)
        service.update = AsyncMock(return_value=sample_publication)
        
        # Act
        result = await service.update_status(1, "enriched")
        
        # Assert
        service.update.assert_called_once_with(1, {"status": "enriched"})
    
    @pytest.mark.asyncio
    async def test_update_status_invalid_status_fails(
        self,
        mock_db_session
    ):
        """Test updating with invalid status fails."""
        # Arrange
        service = PublicationService(mock_db_session)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid status"):
            await service.update_status(1, "invalid_status")
    
    @pytest.mark.asyncio
    async def test_get_pending_enrichment(
        self,
        mock_db_session,
        sample_publication
    ):
        """Test getting publications pending enrichment."""
        # Arrange
        service = PublicationService(mock_db_session)
        service.repository.get_by_status = AsyncMock(return_value=[sample_publication])
        
        # Act
        result = await service.get_pending_enrichment(limit=50)
        
        # Assert
        assert len(result) == 1
        service.repository.get_by_status.assert_called_once_with(
            'pending_enrichment',
            skip=0,
            limit=50
        )
    
    @pytest.mark.asyncio
    async def test_search_full_text(
        self,
        mock_db_session,
        sample_publication
    ):
        """Test full-text search."""
        # Arrange
        service = PublicationService(mock_db_session)
        service.repository.search = AsyncMock(return_value=[sample_publication])
        
        # Act
        result = await service.search_full_text("machine learning", skip=0, limit=10)
        
        # Assert
        assert len(result) == 1
        service.repository.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_create_duplicate_doi_fails(
        self,
        mock_db_session,
        sample_publication_data,
        sample_publication
    ):
        """Test validation fails with duplicate DOI."""
        # Arrange
        service = PublicationService(mock_db_session)
        service.repository.get_by_doi = AsyncMock(return_value=sample_publication)
        
        # Act & Assert
        with pytest.raises(ValueError, match="DOI.*already exists"):
            await service._validate_create(sample_publication_data)
    
    @pytest.mark.asyncio
    async def test_validate_create_duplicate_arxiv_id_fails(
        self,
        mock_db_session,
        sample_publication_data,
        sample_publication
    ):
        """Test validation fails with duplicate arXiv ID."""
        # Arrange
        service = PublicationService(mock_db_session)
        service.repository.get_by_doi = AsyncMock(return_value=None)
        service.repository.get_by_arxiv_id = AsyncMock(return_value=sample_publication)
        
        # Act & Assert
        with pytest.raises(ValueError, match="arXiv ID.*already exists"):
            await service._validate_create(sample_publication_data)
    
    @pytest.mark.asyncio
    async def test_validate_update_invalid_status_fails(
        self,
        mock_db_session
    ):
        """Test validation fails with invalid status."""
        # Arrange
        service = PublicationService(mock_db_session)
        service.repository.get_by_doi = AsyncMock(return_value=None)
        service.repository.get_by_arxiv_id = AsyncMock(return_value=None)
        
        update_data = {"status": "invalid_status"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid status"):
            await service._validate_update(1, update_data)
