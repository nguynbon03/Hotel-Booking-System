from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from jose import jwt
import os, random

from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.utils.security import authenticate_user, hash_password
from app.utils.jwt import create_access_token, create_refresh_token, create_verification_token, decode_token
from app.utils.dependencies import SessionDep, get_current_user
from app.services.task_queue import enqueue_send_otp_email, enqueue_send_verification_email
from app.core.redis import redis_client
from app.core.config import settings
from app.utils.token_store import blacklist_token

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------- REGISTER ----------------
@router.post("/register", response_model=UserRead)
def register(session: SessionDep, payload: UserCreate):
    existing_user = session.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        email_verified=False
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


# ---------------- REQUEST VERIFY EMAIL ----------------
@router.post("/request-verify-email")
def request_verify_email(session: SessionDep, current_user: User = Depends(get_current_user)):
    if current_user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    token = create_verification_token(str(current_user.id), expires_minutes=60 * 24)
    verification_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token}"

    # gửi mail qua celery
    enqueue_send_verification_email(current_user.email, verification_link, current_user.username)

    return {"msg": "Verification email sent"}


# ---------------- VERIFY EMAIL ----------------
@router.get("/verify-email")
def verify_email(session: SessionDep, token: str = Query(...)):
    try:
        payload = decode_token(token)
        if payload.get("type") != "verify_email":
            raise HTTPException(status_code=400, detail="Invalid token type")
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email_verified = True
    session.add(user)
    session.commit()
    return {"msg": "Email successfully verified"}


# ---------------- LOGIN ----------------
@router.post("/login")
def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username/email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    # Nếu chưa verify → login bình thường
    if not user.email_verified:
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    # Nếu đã verify → gửi OTP
    otp = f"{random.randint(100000, 999999)}"
    key = f"otp:{user.id}"
    redis_client.setex(key, 300, otp)  # 5 phút
    enqueue_send_otp_email(user.email, otp, expires_minutes=5, username=user.username)
    return {"msg": "OTP sent to email", "user_id": str(user.id)}


# ---------------- VERIFY OTP ----------------
@router.post("/verify-otp", response_model=Token)
def verify_otp(user_id: str, code: str, session: SessionDep):
    otp_code = redis_client.get(f"otp:{user_id}")
    if not otp_code or otp_code.decode() != code:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    redis_client.delete(f"otp:{user_id}")
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


# ---------------- LOGOUT ----------------
@router.post("/logout")
def logout(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        now = datetime.utcnow().timestamp()
        ttl = int(exp - now)
        if jti:
            blacklist_token(jti, ttl)
        return {"msg": "Logged out successfully"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
