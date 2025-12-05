from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr

from app.utils.enums import SubscriptionPlan, OrganizationStatus, InvitationStatus


# ==========================
# Base
# ==========================
class OrganizationBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE
    status: OrganizationStatus = OrganizationStatus.TRIAL
    max_properties: int = 1
    max_users: int = 3
    max_rooms_per_property: int = 20
    features_enabled: List[str] = []


# ==========================
# Create
# ==========================
class OrganizationCreate(OrganizationBase):
    pass


# ==========================
# Update
# ==========================
class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    status: Optional[OrganizationStatus] = None
    features_enabled: Optional[List[str]] = None


# ==========================
# Response
# ==========================
class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    owner_id: Optional[uuid.UUID] = None

    class Config:
        orm_mode = True


# ==========================
# Invitation
# ==========================
class InvitationBase(BaseModel):
    email: EmailStr


class InvitationCreate(InvitationBase):
    pass


class InvitationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: EmailStr
    status: InvitationStatus
    invitation_token: str
    created_at: datetime
    expires_at: datetime

    class Config:
        orm_mode = True
