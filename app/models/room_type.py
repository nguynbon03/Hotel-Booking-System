"""
SQLModel definition for Room types.

Each ``RoomType`` belongs to a ``Property``.  It defines a category of rooms
with similar characteristics (e.g. Deluxe Double, Suite).  The ``max_occupancy``
represents the maximum number of guests the room type can accommodate.
"""

from __future__ import annotations

import uuid
from typing import Optional
from sqlmodel import SQLModel, Field


class RoomType(SQLModel, table=True):
    __tablename__ = "room_types"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    name: str
    max_occupancy: int = Field(default=2, ge=1)
    description: Optional[str] = None
    is_active: bool = Field(default=True)