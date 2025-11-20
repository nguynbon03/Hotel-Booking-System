"""
Pydantic schemas for RatePlan resources.

``RatePlanCreate`` defines the data required to create a new rate plan.
The property_id and room_type_id are passed via the path parameters in
the API and thus omitted from the body.  ``RatePlanOut`` is used to
represent a rate plan in responses.
"""

from __future__ import annotations

import uuid
from typing import Optional
from pydantic import BaseModel


class RatePlanCreate(BaseModel):
    name: str
    currency: str = "USD"
    base_price: float
    is_refundable: bool = True
    cancellation_policy: Optional[str] = None


class RatePlanOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    room_type_id: uuid.UUID
    name: str
    currency: str
    base_price: float
    is_refundable: bool
    cancellation_policy: Optional[str]