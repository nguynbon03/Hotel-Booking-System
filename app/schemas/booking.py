from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel
from app.utils.enums import BookingStatus


class BookingBase(BaseModel):
    check_in: date
    check_out: date
    rooms_count: int = 1
    total_price: float
    currency: str = "VND"
    status: BookingStatus = BookingStatus.PENDING

    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None


class BookingCreate(BookingBase):
    property_id: uuid.UUID
    room_type_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None


class BookingUpdate(BaseModel):
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    rooms_count: Optional[int] = None
    status: Optional[BookingStatus] = None
    total_price: Optional[float] = None

    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None


class BookingResponse(BookingBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    property_id: uuid.UUID
    room_type_id: uuid.UUID
    hold_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
