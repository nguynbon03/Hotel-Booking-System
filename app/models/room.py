"""
SQLModel definition for the Room table.

This model extends the upstream Room definition by adding an ``image_url``
attribute to support storing a link to a representative photo of the room.
Having an image URL enables front-end applications to display a picture of
each room.  When no image is supplied, ``image_url`` defaults to ``None``.
"""

from __future__ import annotations

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Room(SQLModel, table=True):
    __tablename__ = "rooms"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    number: str = Field(index=True, nullable=False)
    # Retain a human‑readable type name for backward compatibility.  In the new
    # design, room types are modelled in the ``RoomType`` table and rooms
    # should reference a ``room_type_id`` instead of a free‑form string.  The
    # ``type`` field remains optional but should not be used for relational
    # queries.
    type: str = Field(default="standard")
    # Reference to the ``RoomType`` entity.  This allows grouping rooms of the
    # same category under a single RoomType for pricing, availability and
    # description management.  The field is optional to preserve backwards
    # compatibility with existing data, but new rooms should specify a
    # ``room_type_id``.
    room_type_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="room_types.id", index=True
    )
    # Redundant reference to the property.  Although the property can be
    # inferred via the ``RoomType``, storing it here simplifies queries and
    # enforces data integrity when creating or updating rooms directly.
    property_id: Optional[uuid.UUID] = Field(default=None, foreign_key="properties.id", index=True)
    price_per_night: float = Field(gt=0)
    capacity: int = Field(default=2, ge=1)
    description: Optional[str] = None
    image_url: Optional[str] = Field(
        default=None,
        description="Đường dẫn URL của ảnh phòng.  Front-end dùng để hiển thị hình ảnh."
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)