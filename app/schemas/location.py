from __future__ import annotations
import uuid
from typing import Optional

from pydantic import BaseModel
from app.utils.enums import LocationType


class LocationBase(BaseModel):
    name: str
    slug: str
    type: LocationType = LocationType.CITY
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_code: str = "VN"
    timezone: str = "Asia/Ho_Chi_Minh"
    is_active: bool = True


class LocationCreate(LocationBase):
    parent_id: Optional[uuid.UUID] = None


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    type: Optional[LocationType] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None


class LocationResponse(LocationBase):
    id: uuid.UUID
    parent_id: Optional[uuid.UUID]

    class Config:
        orm_mode = True
