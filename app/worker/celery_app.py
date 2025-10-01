# app/worker/celery_app.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "hotel_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],  # 👈 bắt buộc
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
