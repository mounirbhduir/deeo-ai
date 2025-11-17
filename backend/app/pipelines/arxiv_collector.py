"""ArXiv API client with rate limiting and retry logic.

This module provides a robust client for collecting papers from the arXiv API
with proper rate limiting, retry logic, and error handling.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from xml.etree import ElementTree as ET

import aiohttp
from aiolimiter import AsyncLimiter
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.logging import get_logger

logger = get_logger(__name__)


class ArxivCollectorError(Exception):
    """Base exception for ArXiv collector errors."""
    pass


class ArxivAPIError(ArxivCollectorError):
    """Exception raised when arXiv API returns an error."""
    pass


class ArxivRateLimitError(ArxivCollectorError):
    """Exception raised when rate limit is exceeded."""
    pass


class ArxivCollector:
    """Client for collecting papers from arXiv API.

    Features:
    - Rate limiting (1 request per 3 seconds)
    - Automatic retry with exponential backoff
    - Support for multiple search categories
    - Date range filtering
    - Bulk fetching by arXiv IDs

    Supported categories:
    - cs.AI: Artificial Intelligence
    - cs.LG: Machine Learning
    - cs.CV: Computer Vision
    - cs.CL: Computation and Language
    - cs.NE: Neural and Evolutionary Computing
    - stat.ML: Machine Learning (Statistics)
    """

    BASE_URL = "http://export.arxiv.org/api/query"
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom',
    }

    SUPPORTED_CATEGORIES = [
        'cs.AI', 'cs.LG', 'cs.CV', 'cs.CL', 'cs.NE', 'stat.ML'
    ]

    def __init__(
        self,
        rate_limit_requests: int = 1,
        rate_limit_period: float = 3.0,
        max_results_per_request: int = 100,
    ):
        """Initialize ArXiv collector.

        Args:
            rate_limit_requests: Number of requests allowed per period
            rate_limit_period: Time period in seconds for rate limiting
            max_results_per_request: Maximum results per API request
        """
        self.rate_limiter = AsyncLimiter(rate_limit_requests, rate_limit_period)
        self.max_results = max_results_per_request
        self._session: Optional[aiohttp.ClientSession] = None

        logger.info(
            "arxiv.collector.initialized",
            rate_limit=f"{rate_limit_requests}/{rate_limit_period}s",
            max_results=max_results_per_request,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
            self._session = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, ArxivAPIError)),
    )
    async def search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        date_range: Optional[tuple[datetime, datetime]] = None,
        max_results: Optional[int] = None,
        start: int = 0,
    ) -> List[Dict[str, Any]]:
        """Search arXiv for papers matching query.

        Args:
            query: Search query string
            categories: List of arXiv categories to filter by
            date_range: Tuple of (start_date, end_date) for filtering
            max_results: Maximum number of results to return
            start: Starting index for pagination

        Returns:
            List of paper dictionaries with metadata

        Raises:
            ArxivAPIError: If API request fails
            ArxivRateLimitError: If rate limit is exceeded
        """
        # Build search query
        search_query = self._build_query(query, categories, date_range)

        # Set max results
        max_results = max_results or self.max_results

        logger.info(
            "arxiv.search.start",
            query=query,
            categories=categories,
            max_results=max_results,
            start=start,
        )

        # Make API request with rate limiting
        async with self.rate_limiter:
            params = {
                'search_query': search_query,
                'start': start,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending',
            }

            results = await self._make_request(params)

        logger.info(
            "arxiv.search.success",
            count=len(results),
            query=query,
        )

        return results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, ArxivAPIError)),
    )
    async def fetch_by_ids(self, arxiv_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch papers by arXiv IDs.

        Args:
            arxiv_ids: List of arXiv IDs (e.g., ['2311.12345', '2310.98765'])

        Returns:
            List of paper dictionaries with metadata

        Raises:
            ArxivAPIError: If API request fails
        """
        if not arxiv_ids:
            return []

        logger.info("arxiv.fetch_by_ids.start", count=len(arxiv_ids))

        # Build ID list query
        id_list = ','.join(f'"{arxiv_id}"' for arxiv_id in arxiv_ids)
        search_query = f'id_list={id_list}'

        # Make API request with rate limiting
        async with self.rate_limiter:
            params = {
                'id_list': ','.join(arxiv_ids),
                'max_results': len(arxiv_ids),
            }

            results = await self._make_request(params)

        logger.info("arxiv.fetch_by_ids.success", count=len(results))

        return results

    def _build_query(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        date_range: Optional[tuple[datetime, datetime]] = None,
    ) -> str:
        """Build arXiv API search query string.

        Args:
            query: Base search query
            categories: Categories to filter by
            date_range: Date range to filter by

        Returns:
            Formatted query string for arXiv API
        """
        parts = [f'all:{query}']

        # Add category filter
        if categories:
            valid_categories = [
                cat for cat in categories
                if cat in self.SUPPORTED_CATEGORIES
            ]
            if valid_categories:
                cat_query = ' OR '.join(f'cat:{cat}' for cat in valid_categories)
                parts.append(f'({cat_query})')

        # Add date range filter
        if date_range:
            start_date, end_date = date_range
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            parts.append(f'submittedDate:[{start_str} TO {end_str}]')

        return ' AND '.join(parts)

    async def _make_request(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Make HTTP request to arXiv API.

        Args:
            params: Query parameters for API request

        Returns:
            List of parsed paper dictionaries

        Raises:
            ArxivAPIError: If request fails or returns error
        """
        if not self._session:
            raise ArxivCollectorError("Session not initialized. Use async context manager.")

        try:
            async with self._session.get(self.BASE_URL, params=params) as response:
                response.raise_for_status()
                content = await response.text()

                # Parse XML response
                return self._parse_response(content)

        except aiohttp.ClientError as e:
            logger.error("arxiv.request.failed", error=str(e), params=params)
            raise ArxivAPIError(f"API request failed: {e}") from e

    def _parse_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse arXiv API XML response.

        Args:
            xml_content: XML response from arXiv API

        Returns:
            List of paper dictionaries
        """
        try:
            root = ET.fromstring(xml_content)
            entries = root.findall('atom:entry', self.NAMESPACES)

            papers = []
            for entry in entries:
                paper = self._parse_entry(entry)
                if paper:
                    papers.append(paper)

            return papers

        except ET.ParseError as e:
            logger.error("arxiv.parse.failed", error=str(e))
            raise ArxivAPIError(f"Failed to parse XML response: {e}") from e

    def _parse_entry(self, entry: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse a single arXiv entry.

        Args:
            entry: XML element representing a paper

        Returns:
            Paper dictionary or None if parsing fails
        """
        try:
            # Extract arXiv ID from entry ID
            entry_id = entry.find('atom:id', self.NAMESPACES)
            arxiv_id = entry_id.text.split('/')[-1] if entry_id is not None else None

            # Extract basic metadata
            title = entry.find('atom:title', self.NAMESPACES)
            summary = entry.find('atom:summary', self.NAMESPACES)
            published = entry.find('atom:published', self.NAMESPACES)

            # Extract authors
            authors = []
            for author in entry.findall('atom:author', self.NAMESPACES):
                name = author.find('atom:name', self.NAMESPACES)
                if name is not None:
                    authors.append({'name': name.text})

            # Extract categories
            categories = [
                cat.get('term')
                for cat in entry.findall('atom:category', self.NAMESPACES)
                if cat.get('term')
            ]

            # Extract DOI if available
            doi = None
            doi_elem = entry.find('arxiv:doi', self.NAMESPACES)
            if doi_elem is not None:
                doi = doi_elem.text

            return {
                'id': arxiv_id,
                'title': title.text.strip() if title is not None else '',
                'summary': summary.text.strip() if summary is not None else '',
                'authors': authors,
                'categories': categories,
                'published': published.text if published is not None else '',
                'doi': doi,
            }

        except Exception as e:
            logger.warning("arxiv.parse_entry.failed", error=str(e))
            return None
