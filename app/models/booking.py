"""
SQLModel definition for bookings.

This model represents a reservation in the system.  Each booking can
optionally be linked to a user (guest) and must specify the room being
reserved along with the check‑in and check‑out dates.  The status
field tracks the current state of the booking (pending, confirmed,
cancelled, etc.) and timestamps provide auditing information.  The
total_amount stores the cost computed at the time of booking.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field


class BookingStatus(str, Enum):
    """Enumeration of possible booking statuses."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    COMPLETED = "completed"


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Reference to the user who created the booking (nullable to allow guest bookings)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    # Reference to the specific room being booked.  In a more complex design
    # this could reference a RoomType with multiple rooms allocated via inventory.
    room_id: uuid.UUID = Field(foreign_key="rooms.id")
    # Redundant reference to the property that owns the room.  Storing
    # ``property_id`` simplifies analytics and queries without needing to
    # join through the Room or RoomType tables.
    property_id: Optional[uuid.UUID] = Field(default=None, foreign_key="properties.id")
    # Reference to the room type (category) that was booked.  Useful if the
    # booking is associated with a category rather than a specific room (e.g.
    # when rooms are allocated on arrival).  Optional to maintain
    # compatibility with existing bookings that specify only ``room_id``.
    room_type_id: Optional[uuid.UUID] = Field(default=None, foreign_key="room_types.id")
    # Reference to the rate plan used to calculate pricing for this booking.
    rate_plan_id: Optional[uuid.UUID] = Field(default=None, foreign_key="rate_plans.id")
    check_in: date
    check_out: date
    total_amount: float = Field(default=0.0, ge=0.0)
    status: BookingStatus = Field(default=BookingStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Enhanced booking fields for SAAS
    guest_count: int = Field(default=2, ge=1)
    special_requests: Optional[str] = None
    cancellation_reason: Optional[str] = None
    
    # Guest information (for guest bookings)
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None