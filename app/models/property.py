"""
SQLModel definition for Properties.

This model represents a hotel property (hotel, apartment, villa...).  Each property
has a name, optional location and description, an active flag, and a creation
timestamp.  More detailed location information can be stored in a separate
Location model if needed (e.g. country, city, coordinates).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Property(SQLModel, table=True):
    __tablename__ = "properties"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    location: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Multi-tenancy: Properties belong to organizations
    organization_id: uuid.UUID = Field(foreign_key="organizations.id", nullable=False)
    
    # Legacy owner_id for backward compatibility (can be removed later)
    owner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    
    # Enhanced property information for SAAS
    property_type: str = Field(default="HOTEL")  # HOTEL, APARTMENT, VILLA, HOSTEL, etc.
    star_rating: Optional[int] = Field(default=None, ge=1, le=5)
    
    # Contact & Address
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    
    # Coordinates for mapping
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Property settings
    check_in_time: str = Field(default="15:00")
    check_out_time: str = Field(default="11:00")
    currency: str = Field(default="USD")
    
    # Policies
    cancellation_policy: Optional[str] = None
    house_rules: Optional[str] = None
    
    # Media
    main_image_url: Optional[str] = None
    
    # Status tracking
    updated_at: datetime = Field(default_factory=datetime.utcnow)