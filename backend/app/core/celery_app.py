from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "market_state_analysis",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1시간 타임아웃
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Celery Beat 스케줄 설정
celery_app.conf.beat_schedule = {
    "update-all-watchlist-symbols-every-4-hours": {
        "task": "app.tasks.data_update.update_all_watchlist_symbols",
        "schedule": 14400.0,  # 4시간마다 (초 단위)
    },
    "cleanup-old-data-daily": {
        "task": "app.tasks.data_update.cleanup_old_data",
        "schedule": 86400.0,  # 24시간마다 (초 단위)
        "options": {"expires": 3600},
    },
}
