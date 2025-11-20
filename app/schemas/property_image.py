"""
Pydantic schemas for property images.

These schemas are used when creating and returning images associated
with properties.  ``PropertyImageCreate`` accepts fields for new
entries, while ``PropertyImageOut`` is returned from the API and
includes all model attributes.
"""

from __future__ import annotations

import uuid
from typing import Optional
from pydantic import BaseModel


class PropertyImageCreate(BaseModel):
    property_id: uuid.UUID
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    sort_order: int = 0


class PropertyImageOut(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    url: str
    alt_text: Optional[str]
    is_primary: bool
    sort_order: int