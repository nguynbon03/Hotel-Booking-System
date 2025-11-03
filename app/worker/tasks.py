from .celery_app import celery
from app.services.mail_service import send_mail

@celery.task(name="tasks.send_email")
def send_email(to: str, subject: str, html: str):
    send_mail(to, subject, html)

@celery.task(name="tasks.send_invoice")
def send_invoice(to: str, booking_id: str, amount: float):
    html = f"<h3>Invoice</h3><p>Booking: {booking_id}</p><p>Amount: ${amount:.2f}</p>"
    send_mail(to, "Your Hotel Invoice", html)
