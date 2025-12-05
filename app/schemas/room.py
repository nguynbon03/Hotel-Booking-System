from __future__ import annotations
import uuid
from typing import Optional

from pydantic import BaseModel


class RoomBase(BaseModel):
    room_number: str
    floor: Optional[int] = None
    is_active: bool = True


class RoomCreate(RoomBase):
    room_type_id: uuid.UUID


class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    floor: Optional[int] = None
    is_active: Optional[bool] = None


class RoomResponse(RoomBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
