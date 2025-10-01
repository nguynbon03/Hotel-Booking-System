# app/services/mail_service.py
import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
load_dotenv()   # nó sẽ tự đọc file .env

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_STARTTLS=(os.getenv("MAIL_STARTTLS", "True") or "True").lower() in ["true", "1"],
    MAIL_SSL_TLS=(os.getenv("MAIL_SSL_TLS", "False") or "False").lower() in ["true", "1"],
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)


async def send_verification_email(email: str, verification_link: str, username: str | None = None):
    """Gửi email xác thực (link)."""
    username_safe = username or "User"
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #222;">
        <h2>Xin chào {username_safe},</h2>
        <p>Cảm ơn bạn đã đăng ký tại <b>{os.getenv('PROJECT_NAME','OurApp')}</b>.</p>
        <p>Vui lòng nhấn vào nút dưới đây để xác nhận email của bạn:</p>
        <p style="text-align:center;">
          <a href="{verification_link}" style="background:#2563eb;color:#fff;padding:10px 18px;border-radius:6px;text-decoration:none;">
            Xác nhận Email
          </a>
        </p>
        <p>Nếu nút không hoạt động, copy link sau và dán vào trình duyệt:</p>
        <p><small>{verification_link}</small></p>
        <hr>
        <p style="color:#666;font-size:12px;">Nếu bạn không yêu cầu, bạn có thể bỏ qua email này.</p>
      </body>
    </html>
    """
    message = MessageSchema(
        subject="Xác nhận email của bạn",
        recipients=[email],
        body=html,
        subtype="html",
    )
    await fm.send_message(message)


async def send_otp_email(email: str, otp_code: str, expires_minutes: int = 5, username: str | None = None):
    """Gửi OTP ngắn (HTML)."""
    username_safe = username or "User"
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #222;">
        <h3>Xin chào {username_safe},</h3>
        <p>Mã OTP của bạn là:</p>
        <p style="font-size:28px; font-weight:700; letter-spacing:2px;">{otp_code}</p>
        <p>Mã có hiệu lực trong <b>{expires_minutes} phút</b>.</p>
        <p>Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email.</p>
        <hr>
        <p style="color:#666; font-size:12px;">Đừng chia sẻ mã cho người khác.</p>
      </body>
    </html>
    """
    message = MessageSchema(
        subject="Mã OTP xác thực đăng nhập",
        recipients=[email],
        body=html,
        subtype="html",
    )
    await fm.send_message(message)
