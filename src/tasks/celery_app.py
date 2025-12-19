"""
Celery Application - Async Task Processing
Configured for Docker with Redis backend
"""
from celery import Celery
from celery.schedules import crontab
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Celery with Redis
celery_app = Celery(
    "pca_agent",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

# Configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Low traffic, process one at a time
    worker_max_tasks_per_child=100,
    worker_disable_rate_limits=False,
    
    # Result backend settings
    result_expires=86400,  # Results expire after 24 hours
    result_persistent=True,
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Periodic tasks (scheduled jobs)
celery_app.conf.beat_schedule = {
    # Daily cleanup at 2 AM
    "cleanup-old-reports": {
        "task": "src.tasks.maintenance.cleanup_old_reports",
        "schedule": crontab(hour=2, minute=0),
    },
    
    # Refresh benchmarks daily at midnight
    "refresh-benchmarks": {
        "task": "src.tasks.maintenance.refresh_benchmarks",
        "schedule": crontab(hour=0, minute=0),
    },
    
    # Health check every 5 minutes
    "health-check": {
        "task": "src.tasks.maintenance.health_check",
        "schedule": crontab(minute="*/5"),
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "src.tasks.analytics",
    "src.tasks.maintenance",
    "src.tasks.reports"
])

logger.info("Celery app initialized")
