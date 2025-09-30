from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.database import get_session
from app.models.user import User
from app.services.user_service import get_user_by_id
from app.utils.jwt import decode_token
from app.core.database import get_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SessionDep = Annotated[Session, Depends(get_session)]

def get_current_user(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        payload = decode_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise ValueError("Missing subject")
        user_id = UUID(str(subject))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_superuser(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return current_user

