from __future__ import annotations
import uuid
from typing import Optional
from pydantic import BaseModel


class CancellationPolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    free_cancellation_until_hours: Optional[int] = None
    penalty_percent: Optional[float] = None


class CancellationPolicyCreate(CancellationPolicyBase):
    pass


class CancellationPolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    free_cancellation_until_hours: Optional[int] = None
    penalty_percent: Optional[float] = None


class CancellationPolicyResponse(CancellationPolicyBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
