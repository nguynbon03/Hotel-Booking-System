from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.types import Numeric
from sqlmodel import SQLModel, Field, Relationship


class CustomerProfile(SQLModel, table=True):
    __tablename__ = "customer_profiles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", unique=True)

    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    preferred_currency: str = Field(default="USD")
    preferred_language: str = Field(default="en")

    travel_purpose: Optional[str] = None
    special_requests: Optional[str] = None

    loyalty_points: int = Field(default=0)
    loyalty_tier: str = Field(default="BRONZE")

    total_spent: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(14, 2), nullable=False),
    )

    total_bookings: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    user: "User" = Relationship(back_populates="customer_profile")
