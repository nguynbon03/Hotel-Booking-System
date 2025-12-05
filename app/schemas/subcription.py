from __future__ import annotations
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel
from app.utils.enums import (
    SubscriptionPlan,
    SubscriptionStatus,
    BillingCycle,
    InvoiceStatus
)


# ==============================
# Subscription
# ==============================
class SubscriptionBase(BaseModel):
    plan_name: str
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    base_price: Decimal = Decimal("0.00")
    currency: str = "USD"

    status: SubscriptionStatus = SubscriptionStatus.TRIALING

    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None

    cancel_at_period_end: bool = False

    properties_limit: Optional[int] = None
    users_limit: Optional[int] = None
    bookings_limit: Optional[int] = None


class SubscriptionCreate(SubscriptionBase):
    organization_id: uuid.UUID


class SubscriptionResponse(SubscriptionBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ==============================
# Invoice Line Item
# ==============================
class InvoiceLineItemResponse(BaseModel):
    id: uuid.UUID
    description: str
    item_type: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    class Config:
        orm_mode = True


# ==============================
# Invoice
# ==============================
class InvoiceBase(BaseModel):
    invoice_number: str
    status: InvoiceStatus = InvoiceStatus.DRAFT
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str = "USD"

    due_date: date
    period_start: date
    period_end: date


class InvoiceResponse(InvoiceBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    subscription_id: uuid.UUID
    created_at: datetime
    paid_at: Optional[datetime]

    line_items: List[InvoiceLineItemResponse] = []

    class Config:
        orm_mode = True
