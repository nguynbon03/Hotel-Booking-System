from __future__ import annotations
import uuid
from datetime import date
from sqlmodel import SQLModel, Field


class Inventory(SQLModel, table=True):
    __tablename__ = "inventory"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    room_type_id: uuid.UUID = Field(foreign_key="room_types.id")

    date: date
    available_rooms: int  # số phòng còn
