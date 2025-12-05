from __future__ import annotations
import uuid
from typing import Optional, List
from pydantic import BaseModel


class RatePlanBase(BaseModel):
    name: str
    base_price: float
    currency: str = "VND"

    min_days_before_checkin: Optional[int] = None
    max_days_before_checkin: Optional[int] = None
    min_nights: Optional[int] = None
    max_nights: Optional[int] = None
    non_refundable: bool = False
    includes_breakfast: bool = False


class RatePlanCreate(RatePlanBase):
    property_id: uuid.UUID
    room_type_id: uuid.UUID
    cancellation_policy_id: Optional[uuid.UUID] = None


class RatePlanUpdate(BaseModel):
    name: Optional[str] = None
    base_price: Optional[float] = None
    currency: Optional[str] = None
    min_days_before_checkin: Optional[int] = None
    max_days_before_checkin: Optional[int] = None
    min_nights: Optional[int] = None
    max_nights: Optional[int] = None
    non_refundable: Optional[bool] = None
    includes_breakfast: Optional[bool] = None
    cancellation_policy_id: Optional[uuid.UUID] = None


class DailyPriceResponse(BaseModel):
    id: uuid.UUID
    date: str
    price: float

    class Config:
        orm_mode = True


class RatePlanResponse(RatePlanBase):
    id: uuid.UUID
    daily_prices: List[DailyPriceResponse] = []

    class Config:
        orm_mode = True
