from __future__ import annotations
import uuid
from typing import List, Optional

from pydantic import BaseModel


# ==========================
# RoomType Base
# ==========================
class RoomTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    max_occupancy: int = 2
    area_sqm: Optional[float] = None
    is_active: bool = True


class RoomTypeCreate(RoomTypeBase):
    property_id: uuid.UUID


class RoomTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_occupancy: Optional[int] = None
    area_sqm: Optional[float] = None
    is_active: Optional[bool] = None


# ==========================
# Image Response
# ==========================
class RoomTypeImageResponse(BaseModel):
    id: uuid.UUID
    url: str
    is_main: bool = False

    class Config:
        orm_mode = True


# ==========================
# RoomType Response
# ==========================
class RoomTypeResponse(RoomTypeBase):
    id: uuid.UUID
    images: List[RoomTypeImageResponse] = []

    class Config:
        orm_mode = True
