from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt, JWTError

from app.core.config import settings


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expire_delta = timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "type": "access",
        "exp": datetime.now(tz=timezone.utc) + expire_delta,
        "iat": datetime.now(tz=timezone.utc),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str, expires_days: Optional[int] = None) -> str:
    expire_delta = timedelta(days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "exp": datetime.now(tz=timezone.utc) + expire_delta,
        "iat": datetime.now(tz=timezone.utc),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
