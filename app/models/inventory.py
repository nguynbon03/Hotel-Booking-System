"""
SQLModel definition for inventory (availability) records.

The ``Inventory`` table stores the number of rooms available for each
``RoomType`` on a specific date.  It also tracks how many rooms have been
booked and whether the room type is closed for sale on that date.  By
subtracting ``booked_rooms`` from ``total_rooms``, the system can derive
``available_rooms``.
"""

from __future__ import annotations

import uuid
from datetime import date
import uuid
from sqlmodel import SQLModel, Field


class Inventory(SQLModel, table=True):
    __tablename__ = "inventories"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    room_type_id: uuid.UUID = Field(foreign_key="room_types.id", index=True)
    # redundant reference to the property for faster lookup without joining
    property_id: uuid.UUID = Field(foreign_key="properties.id", index=True)
    date: date
    total_rooms: int = Field(default=0, ge=0)
    booked_rooms: int = Field(default=0, ge=0)
    closed_for_sale: bool = Field(default=False)