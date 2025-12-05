from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.types import JSON

from app.utils.enums import SubscriptionPlan, OrganizationStatus, InvitationStatus


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name: str
    slug: str = Field(index=True, unique=True)
    description: Optional[str] = None

    contact_email: str
    contact_phone: Optional[str] = None
    website: Optional[str] = None

    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    subscription_plan: SubscriptionPlan = Field(default=SubscriptionPlan.FREE)
    status: OrganizationStatus = Field(default=OrganizationStatus.TRIAL)

    max_properties: int = Field(default=1)
    max_users: int = Field(default=3)

    features_enabled: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False, default=list)
    )

    owner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    trial_ends_at: Optional[datetime] = None
    subscription_ends_at: Optional[datetime] = None

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    owner: Optional["User"] = Relationship(back_populates="owned_organizations")
    invitations: List["OrganizationInvitation"] = Relationship(back_populates="organization")
    properties: List["Property"] = Relationship(back_populates="organization")
    subscriptions: List["Subscription"] = Relationship(back_populates="organization")


class OrganizationInvitation(SQLModel, table=True):
    __tablename__ = "organization_invitations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    organization_id: uuid.UUID = Field(foreign_key="organizations.id")
    email: str = Field(index=True)

    invited_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    status: InvitationStatus = Field(default=InvitationStatus.PENDING)
    invitation_token: str = Field(index=True, unique=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None

    organization: "Organization" = Relationship(back_populates="invitations")
    invited_by_user: Optional["User"] = Relationship(back_populates="sent_invitations")
