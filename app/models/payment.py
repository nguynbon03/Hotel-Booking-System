from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from app.utils.enums import PaymentStatus


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    booking_id: uuid.UUID = Field(foreign_key="bookings.id")

    amount: float
    currency: str = Field(default="VND")
    provider: str = Field(default="VNPAY")  # hoặc Stripe, Paypal, Momo...
    transaction_id: Optional[str] = None

    status: PaymentStatus = Field(default=PaymentStatus.PENDING)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    booking: "Booking" = Relationship(back_populates="payments")
