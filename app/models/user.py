# app/models/user.py

from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"  # <--- THÊM DÒNG NÀY

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: str = Field(index=True, nullable=False, unique=True)
    username: str = Field(index=True, nullable=False, unique=True)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    email_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)