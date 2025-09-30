from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class AdminUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active:Optional[bool]=None
    is_superuser: Optional[bool]=None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserRead(BaseModel):
    id: UUID
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    email_verified: bool
    created_at: datetime