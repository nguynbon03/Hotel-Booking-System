from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from app.utils.enums import PaymentStatus


class PaymentBase(BaseModel):
    amount: float
    currency: str = "VND"
    status: PaymentStatus = PaymentStatus.PENDING
    provider: Optional[str] = None      # PayOS, Stripe…
    transaction_id: Optional[str] = None


class PaymentCreate(PaymentBase):
    booking_id: uuid.UUID


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None


class PaymentResponse(PaymentBase):
    id: uuid.UUID
    booking_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True
