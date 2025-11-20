"""
Endpoints for availability and pricing quotes.

This router provides a ``POST /availability/quote`` endpoint that allows
clients to request a quote for a room type and rate plan over a
specified date range.  The system checks inventory to determine if
there are enough rooms available for each night of the stay and
calculates the total price using either the rate plan's base price or
per‑date overrides from the DailyPrice table.  If insufficient rooms
are available, the response indicates how many remain and a total price
of 0.0.

Example request body:

```
{
  "property_id": "uuid-of-property",
  "room_type_id": "uuid-of-room-type",
  "rate_plan_id": "uuid-of-rate-plan",
  "check_in": "2025-12-01",
  "check_out": "2025-12-05",
  "num_rooms": 2
}
```

The response will include whether the request is available, how many
rooms remain and the computed total price.
"""

from __future__ import annotations

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.property import Property
from app.models.room_type import RoomType
from app.models.rate_plan import RatePlan
from app.models.inventory import Inventory
from app.models.daily_price import DailyPrice
from app.schemas.availability import QuoteRequest, QuoteResponse


router = APIRouter(prefix="/availability", tags=["availability"])


@router.post("/quote", response_model=QuoteResponse, status_code=status.HTTP_200_OK)
def quote_availability(
    payload: QuoteRequest, session: Session = Depends(get_session)
) -> QuoteResponse:
    """Tính toán báo giá và kiểm tra phòng trống.

    Nhận vào property, room type và rate plan cùng với ngày check-in,
    check-out và số lượng phòng cần đặt.  Hàm này xác định số đêm
    bằng cách tính số ngày giữa check-out và check-in, kiểm tra tồn
    kho từng ngày để đảm bảo có đủ phòng, và tính tổng giá dựa trên
    ``RatePlan.base_price`` hoặc ``DailyPrice.price`` (nếu có override).
    Nếu không đủ phòng, trả về ``available=False`` cùng số phòng còn lại.
    """
    # Validate property
    prop = session.get(Property, payload.property_id)
    if not prop or not getattr(prop, "is_active", True):
        raise HTTPException(status_code=404, detail="Property not found")
    # Validate room type
    room_type = session.get(RoomType, payload.room_type_id)
    if (
        not room_type
        or room_type.property_id != payload.property_id
        or not getattr(room_type, "is_active", True)
    ):
        raise HTTPException(status_code=404, detail="Room type not found for this property")
    # Validate rate plan
    rate_plan = session.get(RatePlan, payload.rate_plan_id)
    if (
        not rate_plan
        or rate_plan.property_id != payload.property_id
        or rate_plan.room_type_id != payload.room_type_id
    ):
        raise HTTPException(status_code=404, detail="Rate plan not found for this room type and property")
    # Validate dates
    if payload.check_out <= payload.check_in:
        raise HTTPException(status_code=400, detail="check_out must be after check_in")
    # Build list of dates (each night of stay)
    nights = (payload.check_out - payload.check_in).days
    dates: List = [payload.check_in + timedelta(days=i) for i in range(nights)]
    # Determine minimum available rooms across dates
    min_available: int = None  # type: ignore
    for day in dates:
        inv = session.exec(
            select(Inventory).where(
                Inventory.room_type_id == payload.room_type_id, Inventory.date == day
            )
        ).first()
        if inv:
            if inv.closed_for_sale:
                # If closed for sale, no rooms available
                min_available = 0
                break
            available = inv.total_rooms - inv.booked_rooms
        else:
            # No inventory record means no rooms defined for this date
            available = 0
        if min_available is None or available < min_available:
            min_available = available
    # If no inventory found at all, treat as zero availability
    available_rooms = min_available if min_available is not None else 0
    # Check if enough rooms remain
    if available_rooms < payload.num_rooms:
        return QuoteResponse(
            available=False,
            remaining_rooms=available_rooms,
            total_price=0.0,
            currency=rate_plan.currency,
        )
    # Calculate total price
    total_price = 0.0
    for day in dates:
        daily_override = session.exec(
            select(DailyPrice).where(
                DailyPrice.rate_plan_id == payload.rate_plan_id, DailyPrice.date == day
            )
        ).first()
        nightly_price = daily_override.price if daily_override else rate_plan.base_price
        total_price += nightly_price * payload.num_rooms
    return QuoteResponse(
        available=True,
        remaining_rooms=available_rooms - payload.num_rooms,
        total_price=total_price,
        currency=rate_plan.currency,
    )