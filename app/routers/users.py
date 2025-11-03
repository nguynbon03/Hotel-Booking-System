from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current

@router.patch("/me", response_model=UserOut)
def update_me(payload: UserUpdate, session: Session = Depends(get_session), current: User = Depends(get_current_user)):
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(current, k, v)
    session.add(current); session.commit(); session.refresh(current)
    return current
