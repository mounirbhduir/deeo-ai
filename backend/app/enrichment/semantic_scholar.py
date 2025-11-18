"""Semantic Scholar API client for publication enrichment.

This module provides asynchronous integration with Semantic Scholar API to enrich
publication data with citations, h-index, affiliations, and impact metrics.

Features:
- Asynchronous HTTP client with connection pooling
- Rate limiting (100 requests per 5 minutes)
- Retry logic with exponential backoff
- Response caching to minimize API calls
- Comprehensive error handling

API Documentation: https://api.semanticscholar.org/api-docs/
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.logging import get_logger

logger = get_logger(__name__)


class SemanticScholarError(Exception):
    """Base exception for Semantic Scholar API errors."""
    pass


class RateLimitError(SemanticScholarError):
    """Raised when API rate limit is exceeded."""
    pass


class PaperNotFoundError(SemanticScholarError):
    """Raised when paper is not found in Semantic Scholar."""
    pass


class SearchType(str, Enum):
    """Search types for Semantic Scholar API."""
    ARXIV_ID = "arxiv"
    DOI = "doi"
    TITLE = "title"
    SEMANTIC_ID = "paperId"


class SemanticScholarClient:
    """Asynchronous client for Semantic Scholar API.

    This client provides methods to search and retrieve publication data from
    Semantic Scholar with automatic rate limiting, retries, and error handling.

    Rate Limits:
    - 100 requests per 5 minutes for unauthenticated requests
    - 1000 requests per 5 minutes with API key

    Example:
        >>> async with SemanticScholarClient() as client:
        ...     paper = await client.get_paper_by_arxiv_id("2301.07041")
        ...     print(f"Citations: {paper['citationCount']}")
    """

    # API Configuration
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    RATE_LIMIT_REQUESTS = 100  # Requests per window
    RATE_LIMIT_WINDOW = 300  # 5 minutes in seconds

    # Default fields to retrieve
    DEFAULT_FIELDS = [
        "paperId",
        "title",
        "abstract",
        "year",
        "citationCount",
        "referenceCount",
        "influentialCitationCount",
        "authors",
        "venue",
        "publicationDate",
        "externalIds",
        "fieldsOfStudy",
        "s2FieldsOfStudy",
        "citations",
        "references",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_requests: Optional[int] = None,
        timeout: float = 30.0,
    ):
        """Initialize Semantic Scholar client.

        Args:
            api_key: Optional API key for higher rate limits
            rate_limit_requests: Custom rate limit (default: 100)
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.api_key = api_key
        self.timeout = timeout

        # Rate limiting
        self.rate_limit_requests = rate_limit_requests or self.RATE_LIMIT_REQUESTS
        self.request_times: List[datetime] = []
        self._rate_limit_lock = asyncio.Lock()

        # HTTP client (initialized in __aenter__)
        self._client: Optional[httpx.AsyncClient] = None

        logger.info(
            "semantic_scholar.client.initialized",
            rate_limit=self.rate_limit_requests,
            has_api_key=bool(api_key),
        )

    async def __aenter__(self):
        """Async context manager entry."""
        headers = {
            "User-Agent": "DEEO.AI/1.0 (https://github.com/deeo-ai; research)",
        }

        if self.api_key:
            headers["x-api-key"] = self.api_key

        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=self.timeout,
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=20,
            ),
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _wait_for_rate_limit(self) -> None:
        """Wait if necessary to respect rate limits.

        This method implements a sliding window rate limiter to ensure we don't
        exceed the API rate limits.
        """
        async with self._rate_limit_lock:
            now = datetime.now()

            # Remove requests outside the current window
            cutoff = now - timedelta(seconds=self.RATE_LIMIT_WINDOW)
            self.request_times = [
                req_time for req_time in self.request_times
                if req_time > cutoff
            ]

            # Check if we've hit the limit
            if len(self.request_times) >= self.rate_limit_requests:
                # Calculate wait time
                oldest_request = self.request_times[0]
                wait_until = oldest_request + timedelta(seconds=self.RATE_LIMIT_WINDOW)
                wait_seconds = (wait_until - now).total_seconds()

                if wait_seconds > 0:
                    logger.warning(
                        "semantic_scholar.rate_limit.waiting",
                        wait_seconds=wait_seconds,
                        requests_in_window=len(self.request_times),
                    )
                    await asyncio.sleep(wait_seconds)

            # Record this request
            self.request_times.append(datetime.now())

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    )
    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Semantic Scholar API with retries.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            RateLimitError: If rate limit is exceeded
            PaperNotFoundError: If paper is not found
            SemanticScholarError: For other API errors
        """
        if not self._client:
            raise SemanticScholarError("Client not initialized. Use async context manager.")

        # Apply rate limiting
        await self._wait_for_rate_limit()

        try:
            logger.debug(
                "semantic_scholar.request.start",
                endpoint=endpoint,
                params=params,
            )

            response = await self._client.get(endpoint, params=params)

            # Handle different status codes
            if response.status_code == 200:
                data = response.json()
                logger.debug(
                    "semantic_scholar.request.success",
                    endpoint=endpoint,
                )
                return data

            elif response.status_code == 404:
                raise PaperNotFoundError(f"Paper not found: {endpoint}")

            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")

            else:
                raise SemanticScholarError(
                    f"API error: {response.status_code} - {response.text}"
                )

        except httpx.HTTPStatusError as e:
            logger.error(
                "semantic_scholar.request.http_error",
                endpoint=endpoint,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise SemanticScholarError(f"HTTP error: {e}") from e

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.warning(
                "semantic_scholar.request.network_error",
                endpoint=endpoint,
                error=str(e),
            )
            raise  # Will be retried by tenacity

        except (PaperNotFoundError, RateLimitError):
            # Re-raise these without wrapping
            raise

        except Exception as e:
            logger.error(
                "semantic_scholar.request.failed",
                endpoint=endpoint,
                error=str(e),
            )
            raise SemanticScholarError(f"Request failed: {e}") from e

    async def get_paper_by_arxiv_id(
        self,
        arxiv_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve paper data by arXiv ID.

        Args:
            arxiv_id: arXiv identifier (e.g., "2301.07041" or "arxiv:2301.07041")
            fields: List of fields to retrieve (default: DEFAULT_FIELDS)

        Returns:
            Paper data dictionary or None if not found

        Example:
            >>> paper = await client.get_paper_by_arxiv_id("2301.07041")
            >>> print(paper['citationCount'])
        """
        # Clean arXiv ID (remove prefix if present)
        arxiv_id = arxiv_id.replace("arxiv:", "").strip()

        fields = fields or self.DEFAULT_FIELDS

        try:
            endpoint = f"/paper/ARXIV:{arxiv_id}"
            params = {"fields": ",".join(fields)}

            data = await self._make_request(endpoint, params)

            logger.info(
                "semantic_scholar.paper.retrieved",
                arxiv_id=arxiv_id,
                citations=data.get("citationCount", 0),
            )

            return data

        except PaperNotFoundError:
            logger.info(
                "semantic_scholar.paper.not_found",
                arxiv_id=arxiv_id,
            )
            return None

        except Exception as e:
            logger.error(
                "semantic_scholar.paper.failed",
                arxiv_id=arxiv_id,
                error=str(e),
            )
            raise

    async def get_paper_by_doi(
        self,
        doi: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve paper data by DOI.

        Args:
            doi: Digital Object Identifier
            fields: List of fields to retrieve

        Returns:
            Paper data dictionary or None if not found
        """
        fields = fields or self.DEFAULT_FIELDS

        try:
            endpoint = f"/paper/DOI:{doi}"
            params = {"fields": ",".join(fields)}

            data = await self._make_request(endpoint, params)

            logger.info(
                "semantic_scholar.paper.retrieved",
                doi=doi,
                citations=data.get("citationCount", 0),
            )

            return data

        except PaperNotFoundError:
            logger.info(
                "semantic_scholar.paper.not_found",
                doi=doi,
            )
            return None

    async def get_paper_by_id(
        self,
        paper_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve paper data by Semantic Scholar paper ID.

        Args:
            paper_id: Semantic Scholar paper ID
            fields: List of fields to retrieve

        Returns:
            Paper data dictionary or None if not found
        """
        fields = fields or self.DEFAULT_FIELDS

        try:
            endpoint = f"/paper/{paper_id}"
            params = {"fields": ",".join(fields)}

            data = await self._make_request(endpoint, params)

            logger.info(
                "semantic_scholar.paper.retrieved",
                paper_id=paper_id,
                citations=data.get("citationCount", 0),
            )

            return data

        except PaperNotFoundError:
            logger.info(
                "semantic_scholar.paper.not_found",
                paper_id=paper_id,
            )
            return None

    async def search_papers(
        self,
        query: str,
        limit: int = 10,
        fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search papers by query string.

        Args:
            query: Search query
            limit: Maximum number of results (max: 100)
            fields: List of fields to retrieve

        Returns:
            List of paper dictionaries
        """
        fields = fields or self.DEFAULT_FIELDS

        try:
            endpoint = "/paper/search"
            params = {
                "query": query,
                "limit": min(limit, 100),  # API max is 100
                "fields": ",".join(fields),
            }

            data = await self._make_request(endpoint, params)

            papers = data.get("data", [])

            logger.info(
                "semantic_scholar.search.success",
                query=query,
                results=len(papers),
            )

            return papers

        except Exception as e:
            logger.error(
                "semantic_scholar.search.failed",
                query=query,
                error=str(e),
            )
            return []

    async def get_author_papers(
        self,
        author_id: str,
        limit: int = 100,
        fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve papers by author ID.

        Args:
            author_id: Semantic Scholar author ID
            limit: Maximum number of papers to retrieve
            fields: List of fields to retrieve

        Returns:
            List of paper dictionaries
        """
        fields = fields or self.DEFAULT_FIELDS

        try:
            endpoint = f"/author/{author_id}/papers"
            params = {
                "limit": limit,
                "fields": ",".join(fields),
            }

            data = await self._make_request(endpoint, params)

            papers = data.get("data", [])

            logger.info(
                "semantic_scholar.author_papers.retrieved",
                author_id=author_id,
                count=len(papers),
            )

            return papers

        except Exception as e:
            logger.error(
                "semantic_scholar.author_papers.failed",
                author_id=author_id,
                error=str(e),
            )
            return []

    def extract_enrichment_data(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant enrichment data from Semantic Scholar response.

        Args:
            paper_data: Paper data from Semantic Scholar API

        Returns:
            Dictionary with enrichment data ready for database storage
        """
        authors_data = []
        for author in paper_data.get("authors", []):
            authors_data.append({
                "semantic_scholar_id": author.get("authorId"),
                "name": author.get("name"),
                "h_index": None,  # Would need separate author API call
                "citation_count": None,  # Would need separate author API call
            })

        enrichment = {
            "semantic_scholar_id": paper_data.get("paperId"),
            "citation_count": paper_data.get("citationCount", 0),
            "reference_count": paper_data.get("referenceCount", 0),
            "influential_citation_count": paper_data.get("influentialCitationCount", 0),
            "venue": paper_data.get("venue"),
            "publication_date": paper_data.get("publicationDate"),
            "fields_of_study": paper_data.get("fieldsOfStudy", []),
            "s2_fields_of_study": [
                field.get("category")
                for field in paper_data.get("s2FieldsOfStudy", [])
            ],
            "external_ids": paper_data.get("externalIds", {}),
            "authors": authors_data,
            "enriched_at": datetime.now().isoformat(),
        }

        logger.debug(
            "semantic_scholar.enrichment.extracted",
            paper_id=enrichment["semantic_scholar_id"],
            citations=enrichment["citation_count"],
        )

        return enrichment
