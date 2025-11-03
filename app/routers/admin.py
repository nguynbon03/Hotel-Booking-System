from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.utils.security import hash_password
from app.utils.dependencies import get_current_superuser  # ✅ check quyền admin

router = APIRouter(prefix="/admin", tags=["admin"])

# ============================================================
# 👑 Admin User Management (chỉ dành cho Admin)
# ============================================================

@router.get("/users", response_model=List[UserOut])
def list_users(
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """📄 Lấy danh sách toàn bộ user (Admin only)."""
    return session.exec(select(User)).all()


@router.get("/users/{user_id}", response_model=UserOut)
def get_user_detail(
    user_id: str,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """🔍 Xem chi tiết thông tin 1 user theo ID."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """➕ Tạo mới user (Admin only)."""
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    payload: UserUpdate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """✏️ Cập nhật thông tin user (Admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Nếu admin gửi password mới -> hash lại
    data = payload.dict(exclude_unset=True)
    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))

    # ✅ Cập nhật các field còn lại
    for field, value in data.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user



@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
):
    """🗑️ Xóa user (Admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return {"detail": "User deleted successfully"}
