import os
from celery import Celery
from celery.schedules import crontab
from src.config import settings

# In order to allow SQLAlchemy models to be accessed, we might need settings available.

celery_app = Celery(
    "payfast_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.worker.tasks", "src.webhooks.services"]
)

celery_app.conf.update(
    task_routes={
        "src.webhooks.services.dispatch_webhook": {"queue": "high_priority"},
        "src.worker.tasks.expire_collect_requests": {"queue": "maintenance"},
    },
    task_default_queue="default",
    beat_schedule={
        "expire-collect-requests-every-1-minute": {
            "task": "src.worker.tasks.expire_collect_requests",
            "schedule": crontab(minute="*"), # Every minute
        }
    },
    timezone="UTC",
)
