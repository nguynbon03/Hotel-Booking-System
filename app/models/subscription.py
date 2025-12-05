from __future__ import annotations
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import Column
from sqlalchemy.types import Numeric
from sqlmodel import SQLModel, Field, Relationship

from app.utils.enums import SubscriptionStatus, BillingCycle, InvoiceStatus


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")

    plan_name: str
    billing_cycle: BillingCycle = Field(default=BillingCycle.MONTHLY)

    base_price: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(12, 2))
    )

    currency: str = Field(default="USD")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.TRIALING)

    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None

    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None

    cancel_at_period_end: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    organization: "Organization" = Relationship(back_populates="subscriptions")
    invoices: List["Invoice"] = Relationship(back_populates="subscription")


class Invoice(SQLModel, table=True):
    __tablename__ = "invoices"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    organization_id: uuid.UUID = Field(foreign_key="organizations.id")
    subscription_id: uuid.UUID = Field(foreign_key="subscriptions.id")

    invoice_number: str = Field(index=True, unique=True)
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT)

    subtotal: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(12, 2)),
    )
    tax_amount: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(12, 2)),
    )
    total_amount: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(12, 2)),
    )

    currency: str = Field(default="USD")

    due_date: date
    period_start: date
    period_end: date
    paid_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    subscription: "Subscription" = Relationship(back_populates="invoices")
