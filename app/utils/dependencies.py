from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.database import get_session
from app.core.redis import is_token_blacklisted
from app.models.user import User
from app.utils.enums import UserRole  # Enum chứa ADMIN, STAFF, CUSTOMER,...

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ============================================================
# 🧱 1️⃣ Base: get_current_user → decode JWT, validate token
# ============================================================
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("scope") != "access":
            raise credentials_exception
        if is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token revoked")

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============================================================
# 🔒 2️⃣ get_active_user → chỉ user còn hoạt động mới được dùng
# ============================================================
def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user. Please contact administrator."
        )
    return current_user


# ============================================================
# 👨‍💼 3️⃣ get_current_staff → nhân viên hoặc admin đều pass
# ============================================================
def get_current_staff(current_user: User = Depends(get_active_user)) -> User:
    if current_user.role.lower() not in [UserRole.STAFF.value.lower(), UserRole.ADMIN.value.lower()]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required."
        )
    return current_user


# ============================================================
# 👑 4️⃣ get_current_superuser → chỉ ADMIN mới được phép
# ============================================================
def get_current_superuser(current_user: User = Depends(get_active_user)) -> User:
    if current_user.role.lower() != UserRole.ADMIN.value.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return current_user
