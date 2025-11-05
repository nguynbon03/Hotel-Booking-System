from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from jose import jwt, JWTError
from datetime import datetime, timezone
from app.core.database import get_session
from app.schemas.auth import RegisterIn, TokenPair, RefreshIn
from app.schemas.user import UserOut
from app.models.user import User
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.redis import add_to_blacklist

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(payload: RegisterIn, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == payload.email)).first():
        raise HTTPException(400, "Email exists")
    user = User(email=payload.email, password_hash=hash_password(payload.password), full_name=payload.full_name,phone=payload.phone)
    session.add(user); session.commit(); session.refresh(user)
    return user

@router.post("/login", response_model=TokenPair)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    if not user.is_active:
        raise HTTPException(403, "Inactive user")

    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        full_name=user.full_name,
        email=user.email
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshIn, session: Session = Depends(get_session)):
    try:
        data = jwt.decode(payload.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if data.get("scope") != "refresh":
            raise HTTPException(401, "Invalid scope")
    except JWTError:
        raise HTTPException(401, "Invalid token")

    uid = data["sub"]
    user = session.exec(select(User).where(User.id == uid)).first()
    if not user:
        raise HTTPException(404, "User not found")

    return TokenPair(
        access_token=create_access_token(str(user.id), user.role),
        refresh_token=create_refresh_token(str(user.id)),
        role=user.role,
        full_name=user.full_name,
        email=user.email
    )


@router.post("/logout")
def logout(refresh: RefreshIn):
    # Blacklist refresh token đến khi hết hạn
    data = jwt.get_unverified_claims(refresh.refresh_token)
    exp = int(data.get("exp", datetime.now(tz=timezone.utc).timestamp()))
    ttl = exp - int(datetime.now(tz=timezone.utc).timestamp())
    add_to_blacklist(refresh.refresh_token, max(ttl, 60))
    return {"message": "logged out"}
