"""
SQLModel definition for Organizations (Multi-tenancy support).

Each organization represents a hotel chain, property management company, 
or individual hotel owner in the SAAS platform. This enables multi-tenancy
where different organizations can manage their own properties, users, and bookings
independently while sharing the same platform infrastructure.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum


class SubscriptionPlan(str, Enum):
    """Available subscription plans for organizations."""
    FREE = "FREE"           # Limited features, 1 property
    BASIC = "BASIC"         # Up to 5 properties
    PROFESSIONAL = "PROFESSIONAL"  # Up to 25 properties
    ENTERPRISE = "ENTERPRISE"      # Unlimited properties


class OrganizationStatus(str, Enum):
    """Organization account status."""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TRIAL = "TRIAL"
    EXPIRED = "EXPIRED"


class Organization(SQLModel, table=True):
    """
    Organization model for multi-tenant SAAS architecture.
    
    Each organization can have multiple properties, users, and manage
    their own booking operations independently.
    """
    __tablename__ = "organizations"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False)  # URL-friendly identifier
    description: Optional[str] = None
    
    # Contact Information
    contact_email: str = Field(nullable=False)
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    
    # Address
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    
    # Subscription & Billing
    subscription_plan: SubscriptionPlan = Field(default=SubscriptionPlan.FREE)
    status: OrganizationStatus = Field(default=OrganizationStatus.TRIAL)
    trial_ends_at: Optional[datetime] = None
    subscription_ends_at: Optional[datetime] = None
    
    # Limits based on subscription
    max_properties: int = Field(default=1)
    max_users: int = Field(default=5)
    max_rooms_per_property: int = Field(default=10)
    
    # Features enabled
    features_enabled: str = Field(default="basic")  # JSON string of enabled features
    
    # Owner reference
    owner_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    
    # Metadata
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = Field(default="#3B82F6")  # Default blue
    secondary_color: Optional[str] = Field(default="#1F2937")  # Default gray


class OrganizationMember(SQLModel, table=True):
    """
    Junction table for organization membership with roles.
    
    Allows users to be members of multiple organizations with different roles.
    """
    __tablename__ = "organization_members"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    
    # Role within the organization
    role: str = Field(default="MEMBER")  # OWNER, ADMIN, MANAGER, STAFF, MEMBER
    
    # Permissions
    can_manage_properties: bool = Field(default=False)
    can_manage_bookings: bool = Field(default=True)
    can_manage_users: bool = Field(default=False)
    can_view_analytics: bool = Field(default=False)
    can_manage_billing: bool = Field(default=False)
    
    # Status
    is_active: bool = Field(default=True)
    invited_at: datetime = Field(default_factory=datetime.utcnow)
    joined_at: Optional[datetime] = None
    
    # Unique constraint to prevent duplicate memberships
    __table_args__ = {"sqlite_autoincrement": True}


class OrganizationInvitation(SQLModel, table=True):
    """
    Invitations to join an organization.
    
    When an organization admin invites a user, an invitation record is created.
    The invited user can accept/decline the invitation.
    """
    __tablename__ = "organization_invitations"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", nullable=False)
    email: str = Field(nullable=False)
    role: str = Field(default="MEMBER")
    
    # Invitation details
    invited_by: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    invitation_token: str = Field(unique=True, nullable=False)
    
    # Status
    status: str = Field(default="PENDING")  # PENDING, ACCEPTED, DECLINED, EXPIRED
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(nullable=False)
    responded_at: Optional[datetime] = None
