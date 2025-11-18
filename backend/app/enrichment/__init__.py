"""Enrichment module for external data sources.

This module provides integration with external APIs to enrich publication data:
- Semantic Scholar: Citations, h-index, affiliations, impact metrics
- Future: OpenAlex, CrossRef, etc.
"""

from app.enrichment.semantic_scholar import SemanticScholarClient
from app.enrichment.enrichment_service import EnrichmentService

__all__ = [
    "SemanticScholarClient",
    "EnrichmentService",
]
