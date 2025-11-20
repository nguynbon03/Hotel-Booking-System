"""
SQLModel definition for daily pricing.

The ``DailyPrice`` table stores price overrides for a rate plan on
specific dates.  If a rate plan has a base price but certain dates need
different pricing (e.g., weekends, holidays), a DailyPrice record can
override the base price for that date.  The currency should match the
rate plan's currency.
"""

from __future__ import annotations

import uuid
from datetime import date
from sqlmodel import SQLModel, Field


class DailyPrice(SQLModel, table=True):
    __tablename__ = "daily_prices"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rate_plan_id: uuid.UUID = Field(foreign_key="rate_plans.id", index=True)
    date: date
    price: float = Field(gt=0)
    currency: str = Field(default="USD")