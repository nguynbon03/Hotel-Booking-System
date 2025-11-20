from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from typing import Optional
from app.utils.enums import UserRole


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str
    full_name: str
    phone: str
    role: UserRole = Field(default=UserRole.CUSTOMER)   # ✅ Enum
    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Multi-tenancy support
    current_organization_id: Optional[uuid.UUID] = Field(
        default=None, 
        foreign_key="organizations.id",
        description="Current active organization for this user session"
    )
    
    # Profile enhancements for SAAS
    avatar_url: Optional[str] = None
    timezone: str = Field(default="UTC")
    language: str = Field(default="en")
    last_login_at: Optional[datetime] = None
    
    # Account status
    is_verified: bool = Field(default=False)  # Overall account verification
    is_suspended: bool = Field(default=False)
    suspended_reason: Optional[str] = None
    suspended_until: Optional[datetime] = None
