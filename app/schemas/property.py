from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from app.utils.enums import PropertyType


# ==========================
# Base
# ==========================
class PropertyBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    star_rating: Optional[int] = None
    property_type: PropertyType = PropertyType.HOTEL
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    currency: str = "USD"
    tax_rate: Optional[float] = None
    service_fee: Optional[float] = None
    cancellation_policy: Optional[str] = None
    house_rules: Optional[str] = None
    main_image_url: Optional[str] = None
    is_active: bool = True


class PropertyCreate(PropertyBase):
    organization_id: uuid.UUID
    location_id: Optional[uuid.UUID] = None


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    star_rating: Optional[int] = None
    property_type: Optional[PropertyType] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    tax_rate: Optional[float] = None
    service_fee: Optional[float] = None
    cancellation_policy: Optional[str] = None
    house_rules: Optional[str] = None
    main_image_url: Optional[str] = None
    is_active: Optional[bool] = None


class PropertyImageResponse(BaseModel):
    id: uuid.UUID
    url: str
    is_main: bool

    class Config:
        orm_mode = True


class PropertyResponse(PropertyBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    images: List[PropertyImageResponse] = []

    class Config:
        orm_mode = True
