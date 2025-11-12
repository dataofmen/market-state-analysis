"""
Celery Worker Entrypoint

Usage:
    celery -A celery_worker worker --loglevel=info

For development with auto-reload:
    watchfiles 'celery -A celery_worker worker --loglevel=info' app/
"""

from app.core.celery_app import celery_app
from app.tasks import data_update  # noqa: F401

__all__ = ["celery_app"]
