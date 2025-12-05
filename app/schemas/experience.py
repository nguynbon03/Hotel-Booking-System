from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ExperienceBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ExperienceCreate(ExperienceBase):
    property_id: uuid.UUID


class ExperienceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ExperienceResponse(ExperienceBase):
    id: uuid.UUID
    property_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
