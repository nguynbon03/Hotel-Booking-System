from app.worker.celery_app import celery

def enqueue_email(to: str, subject: str, html: str):
    celery.send_task("tasks.send_email", args=[to, subject, html])

def enqueue_invoice(to: str, booking_id: str, amount: float):
    celery.send_task("tasks.send_invoice", args=[to, booking_id, amount])
