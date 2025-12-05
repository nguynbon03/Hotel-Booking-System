from __future__ import annotations
import uuid
from typing import Optional
from sqlmodel import SQLModel, Field


class CancellationPolicy(SQLModel, table=True):
    __tablename__ = "cancellation_policies"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: Optional[str] = None

    free_cancellation_until_hours: Optional[int] = None
    penalty_percent: Optional[float] = None
