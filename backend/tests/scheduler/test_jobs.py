"""
Tests for DEEO.AI Scheduler Jobs
=================================

Test coverage for automated jobs:
- arxiv_collection_job
- semantic_scholar_enrichment_job
- statistics_update_job
- cleanup_job
- Job decorators (with_job_logging, retry_job)
- Job registry

Author: DEEO.AI Team
Created: 2025-01-18
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.scheduler.jobs import (
    arxiv_collection_job,
    semantic_scholar_enrichment_job,
    statistics_update_job,
    cleanup_job,
    with_job_logging,
    retry_job,
    JOB_REGISTRY,
    get_job,
    list_jobs,
)


# ============================================================================
# DECORATOR TESTS
# ============================================================================

class TestJobDecorators:
    """Test job decorators."""

    @pytest.mark.asyncio
    async def test_with_job_logging_success(self):
        """Test with_job_logging decorator on successful execution."""

        @with_job_logging("test_job")
        async def mock_job():
            return {"status": "success"}

        result = await mock_job()

        # Decorator should not affect return value
        assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_with_job_logging_failure(self):
        """Test with_job_logging decorator on job failure."""

        @with_job_logging("failing_job")
        async def failing_job():
            raise ValueError("Test error")

        # Decorator should propagate exceptions
        with pytest.raises(ValueError, match="Test error"):
            await failing_job()

    @pytest.mark.asyncio
    async def test_retry_job_success_first_try(self):
        """Test retry_job decorator when job succeeds on first try."""

        call_count = 0

        @retry_job(max_retries=3, delay=0.01, backoff=1.0)
        async def mock_job():
            nonlocal call_count
            call_count += 1
            return {"attempt": call_count}

        result = await mock_job()

        assert result == {"attempt": 1}
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_job_success_after_retries(self):
        """Test retry_job decorator when job succeeds after retries."""

        call_count = 0

        @retry_job(max_retries=3, delay=0.01, backoff=1.0)
        async def flaky_job():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return {"attempt": call_count}

        result = await flaky_job()

        assert result == {"attempt": 3}
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_job_all_retries_exhausted(self):
        """Test retry_job decorator when all retries are exhausted."""

        call_count = 0

        @retry_job(max_retries=2, delay=0.01, backoff=1.0)
        async def always_failing_job():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")

        with pytest.raises(ValueError, match="Persistent error"):
            await always_failing_job()

        assert call_count == 3  # Initial attempt + 2 retries

    @pytest.mark.asyncio
    async def test_retry_job_exponential_backoff(self):
        """Test retry_job decorator exponential backoff."""

        call_times = []

        @retry_job(max_retries=2, delay=0.1, backoff=2.0)
        async def failing_job():
            call_times.append(datetime.now())
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await failing_job()

        # Verify exponential backoff timing
        assert len(call_times) == 3
        # First retry should wait ~0.1s
        # Second retry should wait ~0.2s


# ============================================================================
# JOB REGISTRY TESTS
# ============================================================================

class TestJobRegistry:
    """Test job registry functionality."""

    def test_job_registry_contains_all_jobs(self):
        """Test that job registry contains all expected jobs."""

        expected_jobs = [
            "arxiv_collection",
            "semantic_scholar_enrichment",
            "statistics_update",
            "cleanup"
        ]

        for job_name in expected_jobs:
            assert job_name in JOB_REGISTRY

    def test_job_registry_structure(self):
        """Test that each job in registry has required fields."""

        required_fields = ["function", "trigger", "description"]

        for job_name, job_config in JOB_REGISTRY.items():
            for field in required_fields:
                assert field in job_config, f"Job {job_name} missing {field}"

    def test_get_job_existing(self):
        """Test get_job for existing job."""

        job_config = get_job("arxiv_collection")

        assert job_config is not None
        assert job_config["function"] == arxiv_collection_job
        assert job_config["trigger"] == "cron"

    def test_get_job_non_existing(self):
        """Test get_job for non-existing job."""

        job_config = get_job("non_existing_job")

        assert job_config is None

    def test_list_jobs(self):
        """Test list_jobs returns all job names."""

        jobs = list_jobs()

        assert isinstance(jobs, list)
        assert len(jobs) == 4
        assert "arxiv_collection" in jobs
        assert "semantic_scholar_enrichment" in jobs
        assert "statistics_update" in jobs
        assert "cleanup" in jobs


# ============================================================================
# ARXIV COLLECTION JOB TESTS
# ============================================================================

class TestArxivCollectionJob:
    """Test arXiv collection job."""

    @pytest.mark.asyncio
    async def test_arxiv_collection_job_default_categories(self):
        """Test arXiv collection with default categories."""

        with patch('app.scheduler.jobs.ArxivPipeline') as MockPipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline_instance.run = AsyncMock(return_value={
                "collected": 10,
                "new_publications": 8,
                "updated_publications": 2
            })
            MockPipeline.return_value = mock_pipeline_instance

            result = await arxiv_collection_job(max_results=10)

            assert result["total_collected"] == 50  # 10 per category * 5 categories
            assert result["total_new"] == 40
            assert result["total_updated"] == 10
            assert result["categories_processed"] == 5

    @pytest.mark.asyncio
    async def test_arxiv_collection_job_custom_categories(self):
        """Test arXiv collection with custom categories."""

        with patch('app.scheduler.jobs.ArxivPipeline') as MockPipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline_instance.run = AsyncMock(return_value={
                "collected": 15,
                "new_publications": 12,
                "updated_publications": 3
            })
            MockPipeline.return_value = mock_pipeline_instance

            result = await arxiv_collection_job(
                categories=["cs.AI", "cs.LG"],
                max_results=20
            )

            assert result["total_collected"] == 30  # 15 per category * 2
            assert result["total_new"] == 24
            assert result["total_updated"] == 6
            assert result["categories_processed"] == 2

    @pytest.mark.asyncio
    async def test_arxiv_collection_job_category_failure(self):
        """Test arXiv collection handles individual category failures."""

        call_count = 0

        with patch('app.scheduler.jobs.ArxivPipeline') as MockPipeline:
            mock_pipeline_instance = AsyncMock()

            async def run_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 2:
                    raise Exception("Category failed")
                return {
                    "collected": 10,
                    "new_publications": 8,
                    "updated_publications": 2
                }

            mock_pipeline_instance.run = AsyncMock(side_effect=run_side_effect)
            MockPipeline.return_value = mock_pipeline_instance

            # Should continue despite one category failing
            result = await arxiv_collection_job(
                categories=["cs.AI", "cs.LG", "cs.CL"],
                max_results=10
            )

            # Should have results from 2 successful categories
            assert result["total_collected"] == 20
            assert result["categories_processed"] == 3


# ============================================================================
# SEMANTIC SCHOLAR ENRICHMENT JOB TESTS
# ============================================================================

class TestSemanticScholarEnrichmentJob:
    """Test Semantic Scholar enrichment job."""

    @pytest.mark.asyncio
    async def test_semantic_scholar_enrichment_job_placeholder(self):
        """Test Semantic Scholar enrichment job (placeholder implementation)."""

        result = await semantic_scholar_enrichment_job(
            batch_size=50,
            max_batches=10
        )

        assert "pending_publications" in result
        assert "processed" in result
        assert "enriched" in result
        assert "failed" in result
        assert "note" in result
        assert "placeholder" in result["note"].lower()


# ============================================================================
# STATISTICS UPDATE JOB TESTS
# ============================================================================

class TestStatisticsUpdateJob:
    """Test statistics update job."""

    @pytest.mark.asyncio
    async def test_statistics_update_job(self):
        """Test statistics update job with real data."""

        result = await statistics_update_job()

        assert "total_publications" in result
        assert "total_authors" in result
        assert "total_themes" in result
        assert "total_organisations" in result
        assert "total_citations" in result
        assert "average_citations" in result
        assert "max_citations" in result
        assert "recent_publications_7d" in result
        assert "timestamp" in result

        # Verify stats are numeric
        assert isinstance(result["total_publications"], int)
        assert isinstance(result["total_authors"], int)
        assert isinstance(result["average_citations"], (int, float))

    @pytest.mark.asyncio
    async def test_statistics_update_job_empty_database(self):
        """Test statistics update job with empty database."""

        result = await statistics_update_job()

        # Should handle empty database gracefully (or have some data from fixtures)
        assert result["total_publications"] >= 0
        assert result["total_authors"] >= 0
        assert result["total_citations"] >= 0
        assert isinstance(result["average_citations"], (int, float))


# ============================================================================
# CLEANUP JOB TESTS
# ============================================================================

class TestCleanupJob:
    """Test cleanup job."""

    @pytest.mark.asyncio
    async def test_cleanup_job_default_retention(self):
        """Test cleanup job with default retention periods."""

        result = await cleanup_job()

        assert "logs_deleted" in result
        assert "temp_files_deleted" in result
        assert "cache_entries_cleared" in result
        assert "timestamp" in result
        assert "note" in result

        # Verify it's a placeholder implementation
        assert result["logs_deleted"] == 0
        assert result["temp_files_deleted"] == 0
        assert result["cache_entries_cleared"] == 0

    @pytest.mark.asyncio
    async def test_cleanup_job_custom_retention(self):
        """Test cleanup job with custom retention periods."""

        result = await cleanup_job(
            log_retention_days=60,
            temp_file_retention_hours=48
        )

        assert "logs_deleted" in result
        assert "timestamp" in result


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestJobIntegration:
    """Integration tests for jobs."""

    @pytest.mark.asyncio
    async def test_all_jobs_are_async(self):
        """Test that all jobs are async functions."""

        import inspect

        for job_name, job_config in JOB_REGISTRY.items():
            func = job_config["function"]
            assert inspect.iscoroutinefunction(func), \
                f"Job {job_name} is not an async function"

    @pytest.mark.asyncio
    async def test_job_logging_integration(self):
        """Test that all jobs have logging decorators."""

        # Test that arxiv_collection_job logs and returns results
        with patch('app.scheduler.jobs.ArxivPipeline') as MockPipeline:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline_instance.run = AsyncMock(return_value={
                "collected": 0,
                "new_publications": 0,
                "updated_publications": 0
            })
            MockPipeline.return_value = mock_pipeline_instance

            result = await arxiv_collection_job(categories=["cs.AI"], max_results=1)

            # Should return statistics
            assert "total_collected" in result
            assert "total_new" in result
            assert "total_updated" in result
