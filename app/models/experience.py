from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Experience(SQLModel, table=True):
    __tablename__ = "experiences"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id")

    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    property: "Property" = Relationship(back_populates="experiences")
