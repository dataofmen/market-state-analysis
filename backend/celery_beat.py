"""
Celery Beat Scheduler Entrypoint

Usage:
    celery -A celery_beat beat --loglevel=info
"""

from app.core.celery_app import celery_app
from app.tasks import data_update  # noqa: F401

__all__ = ["celery_app"]
