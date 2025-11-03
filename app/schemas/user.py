from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from app.utils.enums import UserRole

# ============================================================
# 📤 OUTPUT SCHEMA
# ============================================================
class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    phone: str
    role: str
    is_active: bool
    email_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True


# ============================================================
# ✏️ UPDATE SCHEMA
# ============================================================
class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================
# 🧩 CREATE SCHEMA
# ============================================================
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str
    role: str = UserRole.CUSTOMER
    is_active: bool = True
