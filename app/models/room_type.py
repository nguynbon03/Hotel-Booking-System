from __future__ import annotations
import uuid
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class RoomType(SQLModel, table=True):
    __tablename__ = "room_types"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id")

    name: str  # Standard, Deluxe, Luxury
    description: Optional[str] = None

    max_occupancy: int = Field(default=2)
    area_sqm: Optional[float] = None

    is_active: bool = Field(default=True)

    property: "Property" = Relationship(back_populates="room_types")
    rooms: List["Room"] = Relationship(back_populates="room_type")
    images: List["RoomTypeImage"] = Relationship(back_populates="room_type")


class RoomTypeImage(SQLModel, table=True):
    __tablename__ = "room_type_images"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    room_type_id: uuid.UUID = Field(foreign_key="room_types.id")

    url: str
    is_main: bool = Field(default=False)

    room_type: "RoomType" = Relationship(back_populates="images")
