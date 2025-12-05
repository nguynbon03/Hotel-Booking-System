from __future__ import annotations
import uuid
from typing import Optional

from pydantic import BaseModel


# ==========================
# Amenity Base
# ==========================
class AmenityBase(BaseModel):
    name: str
    icon: Optional[str] = None
    type: str = "GENERAL"   # GENERAL / ROOM / PROPERTY


# ==========================
# Create
# ==========================
class AmenityCreate(AmenityBase):
    pass


# ==========================
# Update
# ==========================
class AmenityUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    type: Optional[str] = None


# ==========================
# Response
# ==========================
class AmenityResponse(AmenityBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
