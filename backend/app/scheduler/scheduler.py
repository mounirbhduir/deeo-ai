"""
Configuration APScheduler pour orchestration jobs ETL.

Ce module configure APScheduler avec:
- Backend PostgreSQL pour persistence
- Executor ThreadPoolExecutor pour jobs I/O-bound
- Jobstores pour état jobs
- Monitoring état jobs
"""
from datetime import datetime
from typing import Any, Callable, Dict, Optional, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import (
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR,
    EVENT_JOB_MISSED,
    JobExecutionEvent,
)
from pytz import utc

from app.config import settings
from app.logging.structured_logger import get_logger

logger = get_logger(__name__)


class SchedulerConfig:
    """Configuration APScheduler"""
    
    # PostgreSQL URL pour jobstore
    # Format: postgresql://user:password@host:port/database
    # APScheduler nécessite une URL synchrone (pas asyncpg)
    JOBSTORE_URL = settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    
    # Executors
    EXECUTORS = {
        'default': ThreadPoolExecutor(max_workers=20),
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    
    # Job defaults
    JOB_DEFAULTS = {
        'coalesce': True,           # Combiner plusieurs runs manqués en un seul
        'max_instances': 1,         # Max 1 instance simultanée par job
        'misfire_grace_time': 300,  # 5 minutes de grâce pour runs manqués
    }
    
    # Timezone
    TIMEZONE = utc


class SchedulerManager:
    """
    Manager pour APScheduler.
    
    Responsabilités:
    - Initialisation scheduler
    - Enregistrement jobs
    - Monitoring état jobs
    - Shutdown graceful
    """
    
    def __init__(self):
        """Initialise le scheduler manager"""
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._jobs_registry: Dict[str, Dict[str, Any]] = {}
    
    def initialize(self) -> None:
        """
        Initialise APScheduler avec configuration.
        
        Crée le scheduler avec:
        - Jobstore PostgreSQL
        - Executors configurés
        - Event listeners
        """
        logger.info("scheduler.initializing")
        
        # Jobstores configuration
        jobstores = {
            'default': SQLAlchemyJobStore(url=SchedulerConfig.JOBSTORE_URL)
        }
        
        # Créer scheduler
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=SchedulerConfig.EXECUTORS,
            job_defaults=SchedulerConfig.JOB_DEFAULTS,
            timezone=SchedulerConfig.TIMEZONE
        )
        
        # Ajouter event listeners
        self.scheduler.add_listener(
            self._job_executed_listener,
            EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(
            self._job_error_listener,
            EVENT_JOB_ERROR
        )
        self.scheduler.add_listener(
            self._job_missed_listener,
            EVENT_JOB_MISSED
        )
        
        logger.info("scheduler.initialized", 
                   jobstores=list(jobstores.keys()),
                   executors=list(SchedulerConfig.EXECUTORS.keys()))
    
    def start(self) -> None:
        """
        Démarre le scheduler.
        
        Lance l'exécution des jobs schedulés.
        """
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized. Call initialize() first.")
        
        logger.info("scheduler.starting")
        self.scheduler.start()
        logger.info("scheduler.started", 
                   jobs_count=len(self.scheduler.get_jobs()))
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Arrête le scheduler.
        
        Args:
            wait: Si True, attend la fin des jobs en cours
        """
        if not self.scheduler:
            return
        
        logger.info("scheduler.shutting_down", wait=wait)
        self.scheduler.shutdown(wait=wait)
        logger.info("scheduler.shutdown")
    
    def add_job(
        self,
        func: Callable,
        trigger: str,
        job_id: str,
        name: Optional[str] = None,
        **trigger_kwargs: Any
    ) -> None:
        """
        Ajoute un job au scheduler.
        
        Args:
            func: Fonction à exécuter
            trigger: Type de trigger ('cron', 'interval', 'date')
            job_id: ID unique du job
            name: Nom descriptif du job
            **trigger_kwargs: Arguments du trigger
            
        Example:
            >>> scheduler.add_job(
            ...     func=daily_collection,
            ...     trigger='cron',
            ...     job_id='arxiv_daily',
            ...     name='arXiv Daily Collection',
            ...     hour=2,
            ...     minute=0
            ... )
        """
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")
        
        # Créer trigger
        if trigger == 'cron':
            trigger_obj = CronTrigger(**trigger_kwargs, timezone=utc)
        elif trigger == 'interval':
            trigger_obj = IntervalTrigger(**trigger_kwargs, timezone=utc)
        else:
            raise ValueError(f"Unsupported trigger type: {trigger}")
        
        # Ajouter job
        self.scheduler.add_job(
            func=func,
            trigger=trigger_obj,
            id=job_id,
            name=name or job_id,
            replace_existing=True
        )
        
        # Enregistrer dans registry
        self._jobs_registry[job_id] = {
            'function': func.__name__,
            'trigger': trigger,
            'trigger_kwargs': trigger_kwargs,
            'name': name or job_id,
            'added_at': datetime.now(utc)
        }
        
        logger.info("scheduler.job_added",
                   job_id=job_id,
                   job_name=name or job_id,
                   trigger=trigger,
                   trigger_kwargs=trigger_kwargs)
    
    def remove_job(self, job_id: str) -> None:
        """
        Retire un job du scheduler.
        
        Args:
            job_id: ID du job à retirer
        """
        if not self.scheduler:
            return
        
        self.scheduler.remove_job(job_id)
        self._jobs_registry.pop(job_id, None)
        
        logger.info("scheduler.job_removed", job_id=job_id)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut d'un job.
        
        Args:
            job_id: ID du job
            
        Returns:
            Dictionnaire avec informations job ou None si inexistant
        """
        if not self.scheduler:
            return None
        
        job = self.scheduler.get_job(job_id)
        if not job:
            return None
        
        return {
            'id': job.id,
            'name': job.name,
            'next_run_time': str(job.next_run_time) if hasattr(job, 'next_run_time') and job.next_run_time else None,
            'trigger': str(job.trigger),
            'pending': job.pending
        }
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Liste tous les jobs schedulés.
        
        Returns:
            Liste de dictionnaires avec infos jobs
        """
        if not self.scheduler:
            return []
        
        jobs = self.scheduler.get_jobs()
        return [
            {
                'id': job.id,
                'name': job.name,
                'next_run_time': str(job.next_run_time) if hasattr(job, 'next_run_time') and job.next_run_time else None,
                'trigger': str(job.trigger),
                'pending': job.pending
            }
            for job in jobs
        ]
    
    def pause_job(self, job_id: str) -> None:
        """
        Met en pause un job.
        
        Args:
            job_id: ID du job
        """
        if not self.scheduler:
            return
        
        self.scheduler.pause_job(job_id)
        logger.info("scheduler.job_paused", job_id=job_id)
    
    def resume_job(self, job_id: str) -> None:
        """
        Relance un job en pause.
        
        Args:
            job_id: ID du job
        """
        if not self.scheduler:
            return
        
        self.scheduler.resume_job(job_id)
        logger.info("scheduler.job_resumed", job_id=job_id)
    
    # ===== Event Listeners =====
    
    def _job_executed_listener(self, event: JobExecutionEvent) -> None:
        """
        Listener pour événement job exécuté.
        
        Args:
            event: Événement job exécuté
        """
        logger.info("scheduler.job_executed",
                   job_id=event.job_id,
                   scheduled_run_time=event.scheduled_run_time,
                   return_value=event.retval)
    
    def _job_error_listener(self, event: JobExecutionEvent) -> None:
        """
        Listener pour événement erreur job.
        
        Args:
            event: Événement erreur
        """
        logger.error("scheduler.job_error",
                    job_id=event.job_id,
                    exception=str(event.exception),
                    traceback=event.traceback,
                    exc_info=True)
    
    def _job_missed_listener(self, event: JobExecutionEvent) -> None:
        """
        Listener pour événement job manqué.
        
        Args:
            event: Événement job manqué
        """
        logger.warning("scheduler.job_missed",
                      job_id=event.job_id,
                      scheduled_run_time=event.scheduled_run_time)


# ===== Instance Globale =====

# Singleton scheduler manager
scheduler_manager = SchedulerManager()


def get_scheduler() -> SchedulerManager:
    """
    Récupère l'instance scheduler manager.
    
    Returns:
        Instance SchedulerManager
    """
    return scheduler_manager
