"""
Module scheduler pour DEEO.AI.

Ce module fournit APScheduler configuré avec PostgreSQL
pour l'orchestration des jobs ETL.
"""
from app.scheduler.scheduler import (
    SchedulerManager,
    SchedulerConfig,
    get_scheduler,
    scheduler_manager,
)

from app.scheduler.jobs import (
    arxiv_collection_job,
    semantic_scholar_enrichment_job,
    statistics_update_job,
    cleanup_job,
    JOB_REGISTRY,
    get_job,
    list_jobs,
)

__all__ = [
    # Scheduler
    'SchedulerManager',
    'SchedulerConfig',
    'get_scheduler',
    'scheduler_manager',
    # Jobs
    'arxiv_collection_job',
    'semantic_scholar_enrichment_job',
    'statistics_update_job',
    'cleanup_job',
    'JOB_REGISTRY',
    'get_job',
    'list_jobs',
]
