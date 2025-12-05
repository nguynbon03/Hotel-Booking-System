from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from app.utils.enums import BookingStatus


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    room_type_id: uuid.UUID = Field(foreign_key="room_types.id")

    check_in: date
    check_out: date

    rooms_count: int = Field(default=1)

    total_price: float
    currency: str = Field(default="VND")

    status: BookingStatus = Field(default=BookingStatus.PENDING)

    # Guest info if user did not login
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None

    hold_until: Optional[datetime] = None  # thời gian giữ phòng (hold)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    # RELATIONSHIPS
    user: Optional["User"] = Relationship(back_populates="bookings")
    payments: List["Payment"] = Relationship(back_populates="booking")
