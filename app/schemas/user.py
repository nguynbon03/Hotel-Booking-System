from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from app.utils.enums import UserRole


# ==========================
# Base schema
# ==========================
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    timezone: str = "UTC"
    language: str = "en"
    avatar_url: Optional[str] = None


# ==========================
# Create schema
# ==========================
class UserCreate(UserBase):
    password: str


# ==========================
# Update schema
# ==========================
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


# ==========================
# Response schema
# ==========================
class UserResponse(UserBase):
    id: uuid.UUID
    role: UserRole
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
