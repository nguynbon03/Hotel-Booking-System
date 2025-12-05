from __future__ import annotations
import uuid
from datetime import date

from pydantic import BaseModel


class DailyPriceBase(BaseModel):
    date: date
    price: float


class DailyPriceCreate(DailyPriceBase):
    rate_plan_id: uuid.UUID


class DailyPriceUpdate(BaseModel):
    date: date | None = None
    price: float | None = None


class DailyPriceResponse(DailyPriceBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
