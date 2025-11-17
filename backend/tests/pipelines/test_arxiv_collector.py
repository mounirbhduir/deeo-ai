"""Tests for ArXiv collector."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from app.pipelines.arxiv_collector import (
    ArxivCollector,
    ArxivAPIError,
    ArxivCollectorError,
)


# Mock XML response from arXiv API
MOCK_ARXIV_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2311.12345v1</id>
    <title>Attention Survey</title>
    <summary>This is an abstract about attention mechanisms.</summary>
    <published>2023-11-20T00:00:00Z</published>
    <author><name>John Smith</name></author>
    <author><name>Jane Doe</name></author>
    <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <arxiv:doi>10.48550/arXiv.2311.12345</arxiv:doi>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2311.54321v1</id>
    <title>Deep Learning Review</title>
    <summary>A comprehensive review of deep learning.</summary>
    <published>2023-11-19T00:00:00Z</published>
    <author><name>Alice Johnson</name></author>
    <category term="cs.CV" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>
"""


@pytest.fixture
def collector():
    """Create ArXiv collector instance."""
    return ArxivCollector(rate_limit_requests=1, rate_limit_period=0.1)


@pytest.mark.asyncio
class TestArxivCollector:
    """Test suite for ArxivCollector."""

    async def test_initialization(self, collector):
        """Test collector initialization."""
        assert collector.max_results == 100
        assert collector.rate_limiter is not None
        assert collector._session is None

    async def test_context_manager(self, collector):
        """Test async context manager."""
        async with collector as c:
            assert c._session is not None

        assert collector._session is None

    async def test_search_success(self, collector):
        """Test successful search."""
        async with collector:
            with patch.object(
                collector._session,
                'get',
                return_value=AsyncMock(
                    raise_for_status=Mock(),
                    text=AsyncMock(return_value=MOCK_ARXIV_RESPONSE),
                    __aenter__=AsyncMock(
                        return_value=AsyncMock(
                            raise_for_status=Mock(),
                            text=AsyncMock(return_value=MOCK_ARXIV_RESPONSE),
                        )
                    ),
                    __aexit__=AsyncMock(),
                ),
            ):
                results = await collector.search("deep learning")

                assert len(results) == 2
                assert results[0]['id'] == '2311.12345v1'
                assert results[0]['title'] == 'Attention Survey'
                assert len(results[0]['authors']) == 2
                assert results[0]['categories'] == ['cs.LG', 'cs.AI']

    async def test_search_with_categories(self, collector):
        """Test search with category filtering."""
        query = collector._build_query(
            "machine learning",
            categories=['cs.LG', 'cs.AI'],
        )

        assert 'all:machine learning' in query
        assert 'cat:cs.LG' in query
        assert 'cat:cs.AI' in query

    async def test_search_with_date_range(self, collector):
        """Test search with date range filtering."""
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)

        query = collector._build_query(
            "deep learning",
            date_range=(start_date, end_date),
        )

        assert 'all:deep learning' in query
        assert 'submittedDate:[20230101 TO 20231231]' in query

    async def test_fetch_by_ids_success(self, collector):
        """Test fetching papers by arXiv IDs."""
        async with collector:
            with patch.object(
                collector._session,
                'get',
                return_value=AsyncMock(
                    raise_for_status=Mock(),
                    text=AsyncMock(return_value=MOCK_ARXIV_RESPONSE),
                    __aenter__=AsyncMock(
                        return_value=AsyncMock(
                            raise_for_status=Mock(),
                            text=AsyncMock(return_value=MOCK_ARXIV_RESPONSE),
                        )
                    ),
                    __aexit__=AsyncMock(),
                ),
            ):
                results = await collector.fetch_by_ids(['2311.12345', '2311.54321'])

                assert len(results) == 2

    async def test_fetch_by_ids_empty_list(self, collector):
        """Test fetching with empty ID list."""
        async with collector:
            results = await collector.fetch_by_ids([])
            assert results == []

    async def test_parse_response(self, collector):
        """Test XML response parsing."""
        results = collector._parse_response(MOCK_ARXIV_RESPONSE)

        assert len(results) == 2
        assert results[0]['id'] == '2311.12345v1'
        assert results[0]['title'] == 'Attention Survey'
        assert results[0]['doi'] == '10.48550/arXiv.2311.12345'

    async def test_parse_entry(self, collector):
        """Test single entry parsing."""
        import xml.etree.ElementTree as ET

        root = ET.fromstring(MOCK_ARXIV_RESPONSE)
        entry = root.find('entry', collector.NAMESPACES)

        result = collector._parse_entry(entry)

        assert result is not None
        assert result['id'] == '2311.12345v1'
        assert result['title'] == 'Attention Survey'
        assert len(result['authors']) == 2
        assert result['authors'][0]['name'] == 'John Smith'

    async def test_build_query_with_invalid_categories(self, collector):
        """Test building query with invalid categories."""
        query = collector._build_query(
            "test",
            categories=['invalid.cat', 'cs.LG'],
        )

        assert 'cat:cs.LG' in query
        assert 'invalid.cat' not in query

    async def test_session_not_initialized_error(self, collector):
        """Test error when session not initialized."""
        with pytest.raises(ArxivCollectorError, match="Session not initialized"):
            await collector._make_request({})
