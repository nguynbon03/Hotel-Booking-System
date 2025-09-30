from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate,AdminUpdate
from app.services.user_service import (
    create_user, delete_user, get_user_by_id, list_users, update_user, update_superuser,
)
from app.utils.dependencies import (
    SessionDep, get_current_user, get_current_superuser
)

router = APIRouter(prefix="/users", tags=["users"])



@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user



@router.patch("/me", response_model=UserRead)
def update_current_user(
    payload: UserUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    return update_user(session, current_user, payload)



@router.get("/", response_model=list[UserRead])
def list_users_endpoint(
    session: SessionDep,
    _: User = Depends(get_current_superuser),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return list_users(session, offset=offset, limit=limit)



@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def admin_create_user_endpoint(
    payload: UserCreate,
    session: SessionDep,
    _: User = Depends(get_current_superuser),
):
    return create_user(session, payload)



@router.get("/{user_id}", response_model=UserRead)
def get_user_endpoint(
    user_id: UUID,
    session: SessionDep,
    _: User = Depends(get_current_superuser),
):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.patch("/{user_id}", response_model=UserRead)
def update_user_endpoint(
    user_id: UUID,
    payload: AdminUpdate,
    session: SessionDep,
    _: User = Depends(get_current_superuser),
):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return update_superuser(session, user, payload)


# Xoá user bất kỳ
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
    user_id: UUID,
    session: SessionDep,
    _: User = Depends(get_current_superuser),
):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(session, user)
    return None
