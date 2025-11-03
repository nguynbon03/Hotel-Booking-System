from celery import Celery
from app.core.config import settings

celery = Celery(
    "hotel_tasks",
    broker=f"{settings.REDIS_URL}/1",
    backend=f"{settings.REDIS_URL}/1",
)
celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
)
celery.autodiscover_tasks(["app.worker"])
