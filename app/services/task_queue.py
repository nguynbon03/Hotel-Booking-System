# app/services/task_queue.py
from app.worker.tasks import send_verification_email_task, send_otp_email_task

def enqueue_send_verification_email(email: str, verification_link: str, username: str | None = None):
    send_verification_email_task.delay(email, verification_link, username)

def enqueue_send_otp_email(email: str, otp_code: str, expires_minutes: int = 5, username: str | None = None):
    send_otp_email_task.delay(email, otp_code, expires_minutes, username)
