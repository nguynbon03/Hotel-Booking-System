"""
Pydantic schemas for availability and pricing calculations.

``QuoteRequest`` specifies the inputs needed to calculate a booking quote,
including the property, room type, rate plan, dates and number of rooms.
``QuoteResponse`` returns whether the requested rooms are available, how
many rooms remain and the total price for the stay.  Currency reflects
the rate plan's currency.
"""

from __future__ import annotations

import uuid
from typing import Optional
from datetime import date
from pydantic import BaseModel


class QuoteRequest(BaseModel):
    property_id: uuid.UUID
    room_type_id: uuid.UUID
    rate_plan_id: uuid.UUID
    check_in: date
    check_out: date
    num_rooms: int = 1


class QuoteResponse(BaseModel):
    available: bool
    remaining_rooms: int
    total_price: float
    currency: str