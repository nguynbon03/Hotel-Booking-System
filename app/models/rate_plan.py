"""
SQLModel definition for Rate plans.

A ``RatePlan`` defines the pricing strategy for a particular room type and
property.  Examples include flexible rates, non-refundable rates, or rates
that include breakfast.  Each rate plan has a currency and a base price.
More advanced pricing (e.g. per-date price) can be defined in the DailyPrice
table.
"""

from __future__ import annotations

import uuid
from typing import Optional
from sqlmodel import SQLModel, Field


class RatePlan(SQLModel, table=True):
    __tablename__ = "rate_plans"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    room_type_id: uuid.UUID = Field(foreign_key="room_types.id")
    name: str
    currency: str = Field(default="USD")
    base_price: float = Field(gt=0)
    is_refundable: bool = Field(default=True)
    cancellation_policy: Optional[str] = None