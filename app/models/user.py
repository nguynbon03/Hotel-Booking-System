from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from app.utils.enums import UserRole

if TYPE_CHECKING:
    from app.models.organization import Organization, OrganizationInvitation
    from app.models.property import Property
    from app.models.booking import Booking
    from app.models.customer_profile import (
        CustomerProfile, CustomerFavorite, CustomerNotification, PropertyReview
    )


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    email: str = Field(index=True, unique=True)
    password_hash: str

    full_name: Optional[str] = None
    phone: Optional[str] = None

    role: UserRole = Field(default=UserRole.CUSTOMER)

    # STAFF → thuộc đúng 1 property
    staff_property_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="properties.id"
    )

    # ADMIN_ORG → quản lý 1 tổ chức
    current_organization_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="organizations.id"
    )

    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    is_suspended: bool = Field(default=False)
    suspended_reason: Optional[str] = None
    suspended_until: Optional[datetime] = None

    avatar_url: Optional[str] = None
    timezone: str = Field(default="UTC")
    language: str = Field(default="en")

    last_login_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    # RELATIONSHIPS
    staff_property: Optional["Property"] = Relationship(back_populates="staff_members")
    owned_organizations: List["Organization"] = Relationship(back_populates="owner")
    sent_invitations: List["OrganizationInvitation"] = Relationship(back_populates="invited_by_user")

    bookings: List["Booking"] = Relationship(back_populates="user")
    customer_profile: Optional["CustomerProfile"] = Relationship(back_populates="user")
    favorites: List["CustomerFavorite"] = Relationship(back_populates="user")
    notifications: List["CustomerNotification"] = Relationship(back_populates="user")
    customer_reviews: List["PropertyReview"] = Relationship(back_populates="user")
