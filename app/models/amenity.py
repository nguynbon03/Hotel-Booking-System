from __future__ import annotations
import uuid
from typing import Optional
from sqlmodel import SQLModel, Field


class Amenity(SQLModel, table=True):
    __tablename__ = "amenities"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    icon: Optional[str] = None
    type: str = Field(default="GENERAL")   # GENERAL / ROOM / PROPERTY


class PropertyAmenity(SQLModel, table=True):
    __tablename__ = "property_amenities"

    property_id: uuid.UUID = Field(foreign_key="properties.id", primary_key=True)
    amenity_id: uuid.UUID = Field(foreign_key="amenities.id", primary_key=True)
