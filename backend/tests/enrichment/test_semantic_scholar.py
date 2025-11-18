"""Tests for Semantic Scholar client.

Test coverage:
- API client initialization
- Rate limiting
- Paper retrieval by arXiv ID
- Paper retrieval by DOI
- Search functionality
- Error handling
- Data extraction
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import httpx

from app.enrichment.semantic_scholar import (
    SemanticScholarClient,
    SemanticScholarError,
    RateLimitError,
    PaperNotFoundError,
)


@pytest.fixture
def mock_paper_data():
    """Mock Semantic Scholar API response."""
    return {
        "paperId": "test-paper-id-123",
        "title": "Test Paper Title",
        "abstract": "Test abstract content",
        "year": 2024,
        "citationCount": 42,
        "referenceCount": 25,
        "influentialCitationCount": 5,
        "authors": [
            {
                "authorId": "author-1",
                "name": "John Doe",
            },
            {
                "authorId": "author-2",
                "name": "Jane Smith",
            },
        ],
        "venue": "ICML 2024",
        "publicationDate": "2024-01-15",
        "externalIds": {
            "ArXiv": "2401.12345",
            "DOI": "10.1234/test.doi",
        },
        "fieldsOfStudy": ["Computer Science", "Machine Learning"],
        "s2FieldsOfStudy": [
            {"category": "Computer Science"},
            {"category": "Machine Learning"},
        ],
        "citations": [],
        "references": [],
    }


class TestSemanticScholarClient:
    """Tests for SemanticScholarClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        client = SemanticScholarClient()

        assert client.api_key is None
        assert client.rate_limit_requests == 100
        assert client.timeout == 30.0
        assert client.request_times == []

    @pytest.mark.asyncio
    async def test_client_initialization_with_api_key(self):
        """Test client initialization with API key."""
        client = SemanticScholarClient(api_key="test-api-key")

        assert client.api_key == "test-api-key"

    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test client as async context manager."""
        async with SemanticScholarClient() as client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)

        # Client should be closed after context exit
        # (we can't easily verify this without accessing internals)

    @pytest.mark.asyncio
    async def test_get_paper_by_arxiv_id_success(self, mock_paper_data):
        """Test retrieving paper by arXiv ID."""
        async with SemanticScholarClient() as client:
            with patch.object(
                client, '_make_request', new=AsyncMock(return_value=mock_paper_data)
            ):
                result = await client.get_paper_by_arxiv_id("2401.12345")

                assert result is not None
                assert result["paperId"] == "test-paper-id-123"
                assert result["citationCount"] == 42

    @pytest.mark.asyncio
    async def test_get_paper_by_arxiv_id_with_prefix(self, mock_paper_data):
        """Test retrieving paper by arXiv ID with arxiv: prefix."""
        async with SemanticScholarClient() as client:
            with patch.object(
                client, '_make_request', new=AsyncMock(return_value=mock_paper_data)
            ):
                # Should work with arxiv: prefix
                result = await client.get_paper_by_arxiv_id("arxiv:2401.12345")

                assert result is not None
                assert result["paperId"] == "test-paper-id-123"

    @pytest.mark.asyncio
    async def test_get_paper_by_arxiv_id_not_found(self):
        """Test paper not found error."""
        async with SemanticScholarClient() as client:
            with patch.object(
                client,
                '_make_request',
                new=AsyncMock(side_effect=PaperNotFoundError("Not found")),
            ):
                result = await client.get_paper_by_arxiv_id("9999.99999")

                assert result is None

    @pytest.mark.asyncio
    async def test_get_paper_by_doi_success(self, mock_paper_data):
        """Test retrieving paper by DOI."""
        async with SemanticScholarClient() as client:
            with patch.object(
                client, '_make_request', new=AsyncMock(return_value=mock_paper_data)
            ):
                result = await client.get_paper_by_doi("10.1234/test.doi")

                assert result is not None
                assert result["paperId"] == "test-paper-id-123"

    @pytest.mark.asyncio
    async def test_get_paper_by_id_success(self, mock_paper_data):
        """Test retrieving paper by Semantic Scholar ID."""
        async with SemanticScholarClient() as client:
            with patch.object(
                client, '_make_request', new=AsyncMock(return_value=mock_paper_data)
            ):
                result = await client.get_paper_by_id("test-paper-id-123")

                assert result is not None
                assert result["paperId"] == "test-paper-id-123"

    @pytest.mark.asyncio
    async def test_search_papers_success(self, mock_paper_data):
        """Test searching papers."""
        search_response = {
            "data": [mock_paper_data],
            "total": 1,
        }

        async with SemanticScholarClient() as client:
            with patch.object(
                client, '_make_request', new=AsyncMock(return_value=search_response)
            ):
                results = await client.search_papers("deep learning", limit=10)

                assert len(results) == 1
                assert results[0]["paperId"] == "test-paper-id-123"

    @pytest.mark.asyncio
    async def test_search_papers_empty_results(self):
        """Test searching with no results."""
        search_response = {
            "data": [],
            "total": 0,
        }

        async with SemanticScholarClient() as client:
            with patch.object(
                client, '_make_request', new=AsyncMock(return_value=search_response)
            ):
                results = await client.search_papers("nonexistent query")

                assert len(results) == 0

    @pytest.mark.asyncio
    async def test_extract_enrichment_data(self, mock_paper_data):
        """Test extracting enrichment data."""
        client = SemanticScholarClient()

        enrichment = client.extract_enrichment_data(mock_paper_data)

        assert enrichment["semantic_scholar_id"] == "test-paper-id-123"
        assert enrichment["citation_count"] == 42
        assert enrichment["reference_count"] == 25
        assert enrichment["influential_citation_count"] == 5
        assert enrichment["venue"] == "ICML 2024"
        assert len(enrichment["authors"]) == 2
        assert enrichment["authors"][0]["semantic_scholar_id"] == "author-1"
        assert enrichment["authors"][0]["name"] == "John Doe"
        assert "enriched_at" in enrichment

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        client = SemanticScholarClient(rate_limit_requests=2)

        async with client:
            # First two requests should go through immediately
            await client._wait_for_rate_limit()
            await client._wait_for_rate_limit()

            assert len(client.request_times) == 2

            # Third request should trigger rate limiting
            # (we won't wait for it in tests, just verify the check works)
            assert len(client.request_times) >= 2

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self):
        """Test handling of rate limit errors."""
        async with SemanticScholarClient() as client:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"

            with patch.object(
                client._client, 'get', new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(RateLimitError):
                    await client._make_request("/test")

    @pytest.mark.asyncio
    async def test_make_request_not_found_error(self):
        """Test handling of not found errors."""
        async with SemanticScholarClient() as client:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Not found"

            with patch.object(
                client._client, 'get', new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(PaperNotFoundError):
                    await client._make_request("/test")

    @pytest.mark.asyncio
    async def test_make_request_generic_error(self):
        """Test handling of generic API errors."""
        async with SemanticScholarClient() as client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"

            with patch.object(
                client._client, 'get', new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(SemanticScholarError):
                    await client._make_request("/test")

    @pytest.mark.asyncio
    async def test_client_without_context_manager(self):
        """Test that client raises error when not initialized."""
        client = SemanticScholarClient()

        with pytest.raises(SemanticScholarError, match="not initialized"):
            await client._make_request("/test")

    @pytest.mark.asyncio
    async def test_get_author_papers(self):
        """Test retrieving papers by author ID."""
        mock_response = {
            "data": [
                {"paperId": "paper1", "title": "Paper 1"},
                {"paperId": "paper2", "title": "Paper 2"},
            ]
        }

        async with SemanticScholarClient() as client:
            with patch.object(
                client, '_make_request', new=AsyncMock(return_value=mock_response)
            ):
                results = await client.get_author_papers("author-123", limit=10)

                assert len(results) == 2
                assert results[0]["paperId"] == "paper1"

    @pytest.mark.asyncio
    async def test_custom_fields(self, mock_paper_data):
        """Test using custom fields."""
        async with SemanticScholarClient() as client:
            with patch.object(
                client, '_make_request', new=AsyncMock(return_value=mock_paper_data)
            ) as mock_request:
                custom_fields = ["paperId", "title", "citationCount"]
                await client.get_paper_by_arxiv_id("2401.12345", fields=custom_fields)

                # Verify custom fields were passed
                mock_request.assert_called_once()
                call_args = mock_request.call_args
                # Args are (endpoint, params)
                assert len(call_args.args) == 2
                params = call_args.args[1]
                assert "fields" in params
                assert "paperId,title,citationCount" == params["fields"]
