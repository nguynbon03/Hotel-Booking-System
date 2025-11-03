from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid
from app.utils.enums import UserRole

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str
    full_name: str
    phone:str
    role: str = Field(default=UserRole.CUSTOMER)
    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
