"""
Tests for DEEO.AI Scheduler Manager
====================================

Test coverage for APScheduler integration:
- SchedulerManager initialization
- Job addition and removal
- Job scheduling (cron, interval)
- Job execution monitoring
- Event listeners
- Graceful shutdown

Author: DEEO.AI Team
Created: 2025-01-18
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
import asyncio

from apscheduler.events import JobExecutionEvent, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from app.scheduler.scheduler import (
    SchedulerManager,
    SchedulerConfig,
    get_scheduler,
    scheduler_manager,
)


# ============================================================================
# SCHEDULER CONFIG TESTS
# ============================================================================

class TestSchedulerConfig:
    """Test scheduler configuration."""

    def test_jobstore_url_format(self):
        """Test that jobstore URL is in correct format for APScheduler."""

        url = SchedulerConfig.JOBSTORE_URL

        # APScheduler requires postgresql:// not postgresql+asyncpg://
        assert url.startswith("postgresql://")
        assert "asyncpg" not in url

    def test_executors_configuration(self):
        """Test executor configuration."""

        executors = SchedulerConfig.EXECUTORS

        assert "default" in executors
        assert "processpool" in executors

    def test_job_defaults(self):
        """Test job default configuration."""

        defaults = SchedulerConfig.JOB_DEFAULTS

        assert defaults["coalesce"] is True
        assert defaults["max_instances"] == 1
        assert defaults["misfire_grace_time"] == 300


# ============================================================================
# SCHEDULER MANAGER TESTS
# ============================================================================

class TestSchedulerManager:
    """Test scheduler manager."""

    def test_initialization(self):
        """Test scheduler manager initialization."""

        manager = SchedulerManager()

        assert manager.scheduler is None
        assert manager._jobs_registry == {}

    def test_initialize_creates_scheduler(self):
        """Test that initialize creates APScheduler instance."""

        manager = SchedulerManager()
        manager.initialize()

        assert manager.scheduler is not None

        # Only shutdown if started
        if manager.scheduler.running:
            manager.shutdown(wait=False)

    def test_start_without_initialize_raises_error(self):
        """Test that starting without initialize raises error."""

        manager = SchedulerManager()

        with pytest.raises(RuntimeError, match="not initialized"):
            manager.start()

    def test_start_and_shutdown(self):
        """Test scheduler start and shutdown."""

        manager = SchedulerManager()
        manager.initialize()
        manager.start()

        assert manager.scheduler.running

        manager.shutdown(wait=False)

    def test_double_shutdown_safe(self):
        """Test that double shutdown is safe."""

        manager = SchedulerManager()
        manager.initialize()
        manager.start()

        manager.shutdown(wait=False)
        manager.shutdown(wait=False)  # Should not raise error


# ============================================================================
# JOB MANAGEMENT TESTS
# ============================================================================

class TestJobManagement:
    """Test job addition, removal, and management."""

    @pytest.fixture
    def running_scheduler(self):
        """Fixture providing a running scheduler."""

        manager = SchedulerManager()
        manager.initialize()
        manager.start()

        yield manager

        manager.shutdown(wait=False)

    async def dummy_job(self):
        """Dummy async job for testing."""
        return "completed"

    def test_add_cron_job(self, running_scheduler):
        """Test adding a cron job."""

        running_scheduler.add_job(
            func=self.dummy_job,
            trigger="cron",
            job_id="test_cron",
            name="Test Cron Job",
            hour=2,
            minute=0
        )

        assert "test_cron" in running_scheduler._jobs_registry
        job = running_scheduler.scheduler.get_job("test_cron")
        assert job is not None
        assert job.name == "Test Cron Job"

    def test_add_interval_job(self, running_scheduler):
        """Test adding an interval job."""

        running_scheduler.add_job(
            func=self.dummy_job,
            trigger="interval",
            job_id="test_interval",
            name="Test Interval Job",
            hours=1
        )

        assert "test_interval" in running_scheduler._jobs_registry
        job = running_scheduler.scheduler.get_job("test_interval")
        assert job is not None

    def test_add_job_without_name_uses_id(self, running_scheduler):
        """Test that job without name uses job_id as name."""

        running_scheduler.add_job(
            func=self.dummy_job,
            trigger="interval",
            job_id="unnamed_job",
            hours=1
        )

        job = running_scheduler.scheduler.get_job("unnamed_job")
        assert job.name == "unnamed_job"

    def test_add_job_invalid_trigger_raises_error(self, running_scheduler):
        """Test that invalid trigger type raises error."""

        with pytest.raises(ValueError, match="Unsupported trigger type"):
            running_scheduler.add_job(
                func=self.dummy_job,
                trigger="invalid_trigger",
                job_id="test_job"
            )

    def test_remove_job(self, running_scheduler):
        """Test job removal."""

        running_scheduler.add_job(
            func=self.dummy_job,
            trigger="interval",
            job_id="removable_job",
            hours=1
        )

        assert "removable_job" in running_scheduler._jobs_registry

        running_scheduler.remove_job("removable_job")

        assert "removable_job" not in running_scheduler._jobs_registry
        assert running_scheduler.scheduler.get_job("removable_job") is None

    def test_pause_and_resume_job(self, running_scheduler):
        """Test pausing and resuming a job."""

        running_scheduler.add_job(
            func=self.dummy_job,
            trigger="interval",
            job_id="pausable_job",
            seconds=10
        )

        # Pause job
        running_scheduler.pause_job("pausable_job")
        job = running_scheduler.scheduler.get_job("pausable_job")
        assert job.next_run_time is None

        # Resume job
        running_scheduler.resume_job("pausable_job")
        job = running_scheduler.scheduler.get_job("pausable_job")
        assert job.next_run_time is not None


# ============================================================================
# JOB STATUS AND MONITORING TESTS
# ============================================================================

class TestJobStatusMonitoring:
    """Test job status retrieval and monitoring."""

    @pytest.fixture
    def scheduler_with_jobs(self):
        """Fixture with scheduler containing test jobs."""
        from app.scheduler.jobs import cleanup_job, statistics_update_job

        manager = SchedulerManager()
        manager.initialize()
        manager.start()

        manager.add_job(
            func=cleanup_job,
            trigger="interval",
            job_id="job_1",
            name="Job 1",
            hours=1
        )

        manager.add_job(
            func=statistics_update_job,
            trigger="cron",
            job_id="job_2",
            name="Job 2",
            hour=3
        )

        yield manager

        manager.shutdown(wait=False)

    def test_get_job_status_existing(self, scheduler_with_jobs):
        """Test getting status of existing job."""

        status = scheduler_with_jobs.get_job_status("job_1")

        assert status is not None
        assert status["id"] == "job_1"
        assert status["name"] == "Job 1"
        assert "next_run_time" in status
        assert "trigger" in status
        assert "pending" in status

    def test_get_job_status_non_existing(self, scheduler_with_jobs):
        """Test getting status of non-existing job."""

        status = scheduler_with_jobs.get_job_status("non_existing")

        assert status is None

    def test_get_all_jobs(self, scheduler_with_jobs):
        """Test getting all jobs."""

        all_jobs = scheduler_with_jobs.get_all_jobs()

        # Should have test jobs plus any registry jobs loaded during startup
        assert len(all_jobs) >= 2
        job_ids = [job["id"] for job in all_jobs]
        assert "job_1" in job_ids
        assert "job_2" in job_ids


# ============================================================================
# EVENT LISTENER TESTS
# ============================================================================

class TestEventListeners:
    """Test scheduler event listeners."""

    def test_job_executed_listener(self):
        """Test job executed event listener."""

        manager = SchedulerManager()

        event = MagicMock(spec=JobExecutionEvent)
        event.job_id = "test_job"
        event.scheduled_run_time = datetime.now()
        event.retval = {"status": "success"}

        # Should not raise any errors
        manager._job_executed_listener(event)

    def test_job_error_listener(self):
        """Test job error event listener."""

        manager = SchedulerManager()

        event = MagicMock(spec=JobExecutionEvent)
        event.job_id = "test_job"
        event.exception = ValueError("Test error")
        event.traceback = "Traceback..."

        # Should not raise any errors
        manager._job_error_listener(event)

    def test_job_missed_listener(self):
        """Test job missed event listener."""

        manager = SchedulerManager()

        event = MagicMock(spec=JobExecutionEvent)
        event.job_id = "test_job"
        event.scheduled_run_time = datetime.now()

        # Should not raise any errors
        manager._job_missed_listener(event)


# ============================================================================
# GLOBAL SCHEDULER INSTANCE TESTS
# ============================================================================

class TestGlobalSchedulerInstance:
    """Test global scheduler instance."""

    def test_get_scheduler_returns_singleton(self):
        """Test that get_scheduler returns singleton instance."""

        scheduler1 = get_scheduler()
        scheduler2 = get_scheduler()

        assert scheduler1 is scheduler2

    def test_scheduler_manager_is_singleton(self):
        """Test that scheduler_manager is the singleton instance."""

        assert scheduler_manager is get_scheduler()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestSchedulerIntegration:
    """Integration tests for scheduler."""

    def test_job_registry_persistence(self):
        """Test that job registry persists job information."""
        from app.scheduler.jobs import cleanup_job

        manager = SchedulerManager()
        manager.initialize()
        manager.start()

        manager.add_job(
            func=cleanup_job,
            trigger="interval",
            job_id="persistent_job",
            name="Persistent Job",
            hours=1
        )

        # Check registry
        assert "persistent_job" in manager._jobs_registry
        registry_entry = manager._jobs_registry["persistent_job"]

        assert registry_entry["function"] == "cleanup_job"
        assert registry_entry["trigger"] == "interval"
        assert registry_entry["name"] == "Persistent Job"
        assert "added_at" in registry_entry

        manager.shutdown(wait=False)

    def test_replace_existing_job(self):
        """Test that adding job with same ID replaces existing."""
        from app.scheduler.jobs import cleanup_job, statistics_update_job

        manager = SchedulerManager()
        manager.initialize()
        manager.start()

        manager.add_job(
            func=cleanup_job,
            trigger="interval",
            job_id="versioned_job",
            hours=1
        )

        # Replace with new version
        manager.add_job(
            func=statistics_update_job,
            trigger="interval",
            job_id="versioned_job",
            hours=2
        )

        # Should only have one job
        all_jobs = manager.get_all_jobs()
        job_count = sum(1 for job in all_jobs if job["id"] == "versioned_job")
        assert job_count == 1

        manager.shutdown(wait=False)
