from __future__ import annotations
import uuid
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class RatePlan(SQLModel, table=True):
    __tablename__ = "rate_plans"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    room_type_id: uuid.UUID = Field(foreign_key="room_types.id")

    name: str
    base_price: float
    currency: str = Field(default="VND")

    min_days_before_checkin: Optional[int] = None
    max_days_before_checkin: Optional[int] = None

    min_nights: Optional[int] = None
    max_nights: Optional[int] = None

    non_refundable: bool = Field(default=False)
    includes_breakfast: bool = Field(default=False)

    cancellation_policy_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="cancellation_policies.id"
    )

    daily_prices: List["DailyPrice"] = Relationship(back_populates="rate_plan")
