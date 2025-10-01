# app/worker/tasks.py
from app.worker.celery_app import celery_app
import asyncio
from app.services.mail_service import send_verification_email, send_otp_email

@celery_app.task(name="send_verification_email_task")
def send_verification_email_task(email: str, verification_link: str, username: str | None = None):
    # chạy hàm async trong worker process
    asyncio.run(send_verification_email(email=email, verification_link=verification_link, username=username))


@celery_app.task(name="send_otp_email_task")
def send_otp_email_task(email: str, otp_code: str, expires_minutes: int = 5, username: str | None = None):
    asyncio.run(send_otp_email(email=email, otp_code=otp_code, expires_minutes=expires_minutes, username=username))
