from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.organization import SubscriptionPlan, OrganizationStatus


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    contact_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    slug: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-z0-9-]+$')
    subscription_plan: SubscriptionPlan = Field(default=SubscriptionPlan.FREE)

    @validator('slug')
    def validate_slug(cls, v):
        if v.startswith('-') or v.endswith('-') or '--' in v:
            raise ValueError('Slug cannot start/end with hyphen or contain consecutive hyphens')
        return v.lower()


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    contact_email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    primary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    secondary_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    logo_url: Optional[str] = None


class OrganizationOut(OrganizationBase):
    id: uuid.UUID
    slug: str
    subscription_plan: SubscriptionPlan
    status: OrganizationStatus
    max_properties: int
    max_users: int
    max_rooms_per_property: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    trial_ends_at: Optional[datetime] = None
    subscription_ends_at: Optional[datetime] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True


class OrganizationMemberBase(BaseModel):
    role: str = Field(default="MEMBER")
    can_manage_properties: bool = Field(default=False)
    can_manage_bookings: bool = Field(default=True)
    can_manage_users: bool = Field(default=False)
    can_view_analytics: bool = Field(default=False)
    can_manage_billing: bool = Field(default=False)


class OrganizationMemberCreate(OrganizationMemberBase):
    user_id: uuid.UUID


class OrganizationMemberUpdate(BaseModel):
    role: Optional[str] = None
    can_manage_properties: Optional[bool] = None
    can_manage_bookings: Optional[bool] = None
    can_manage_users: Optional[bool] = None
    can_view_analytics: Optional[bool] = None
    can_manage_billing: Optional[bool] = None
    is_active: Optional[bool] = None


class OrganizationMemberOut(OrganizationMemberBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool
    invited_at: datetime
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationInvitationCreate(BaseModel):
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    role: str = Field(default="MEMBER")


class OrganizationInvitationOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    role: str
    status: str
    created_at: datetime
    expires_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvitationResponse(BaseModel):
    action: str = Field(..., pattern=r'^(accept|decline)$')


class SubscriptionUpdate(BaseModel):
    subscription_plan: SubscriptionPlan
    subscription_ends_at: Optional[datetime] = None


class OrganizationStats(BaseModel):
    total_properties: int
    total_rooms: int
    total_bookings: int
    total_revenue: float
    active_bookings: int
    occupancy_rate: float

    properties_used: int
    properties_limit: int
    users_used: int
    users_limit: int


class OrganizationSwitch(BaseModel):
    organization_id: uuid.UUID


class BulkMemberUpdate(BaseModel):
    member_ids: List[uuid.UUID]
    updates: OrganizationMemberUpdate


class OrganizationSearch(BaseModel):
    query: Optional[str] = None
    status: Optional[OrganizationStatus] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    country: Optional[str] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)
