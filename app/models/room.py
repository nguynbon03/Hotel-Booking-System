from __future__ import annotations
import uuid
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Room(SQLModel, table=True):
    __tablename__ = "rooms"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    room_type_id: uuid.UUID = Field(foreign_key="room_types.id")

    room_number: str
    floor: Optional[int] = None
    is_active: bool = Field(default=True)

    room_type: "RoomType" = Relationship(back_populates="rooms")
