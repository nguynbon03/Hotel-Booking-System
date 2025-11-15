from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.utils.dependencies import get_active_user   # 🔥 dùng get_active_user
from app.utils.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


# ============================================================
# 📌 GET /users/me — chỉ active user mới được truy cập
# ============================================================
@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_active_user)):
    return current


# ============================================================
# 📌 PATCH /users/me — update email, password, full_name, phone
# ============================================================
@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    session: Session = Depends(get_session),
    current: User = Depends(get_active_user),
):
    # ✨ data chứa những field user đã gửi (bỏ None)
    data = payload.model_dump(exclude_unset=True)

    # 1️⃣ Nếu user đổi email → check duplicate
    if "email" in data and data["email"] != current.email:
        exists = session.exec(
            select(User).where(User.email == data["email"])
        ).first()
        if exists:
            raise HTTPException(400, detail="Email already exists")

    # 2️⃣ Hash password nếu có gửi
    if "password" in data:
        current.password_hash = hash_password(data["password"])
        del data["password"]

    # 3️⃣ Update các field còn lại (full_name, phone,…)
    for key, value in data.items():
        setattr(current, key, value)

    # 4️⃣ Save DB
    session.add(current)
    session.commit()
    session.refresh(current)

    return current
