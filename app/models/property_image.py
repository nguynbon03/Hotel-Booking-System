"""
SQLModel definition for Property Images.

This model represents images associated with a property.
Each property can have multiple images for showcasing rooms, amenities, and facilities.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class PropertyImage(SQLModel, table=True):
    __tablename__ = "property_images"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id", index=True)
    image_url: str = Field(description="URL of the image")
    alt_text: Optional[str] = Field(default=None, description="Alternative text for accessibility")
    caption: Optional[str] = Field(default=None, description="Image caption")
    display_order: int = Field(default=0, description="Order for displaying images")
    is_primary: bool = Field(default=False, description="Whether this is the primary image")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)