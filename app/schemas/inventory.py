from __future__ import annotations
import uuid
from datetime import date
from pydantic import BaseModel


class InventoryBase(BaseModel):
    date: date
    available_rooms: int


class InventoryCreate(InventoryBase):
    room_type_id: uuid.UUID


class InventoryUpdate(BaseModel):
    available_rooms: int | None = None


class InventoryResponse(InventoryBase):
    id: uuid.UUID
    room_type_id: uuid.UUID

    class Config:
        orm_mode = True
