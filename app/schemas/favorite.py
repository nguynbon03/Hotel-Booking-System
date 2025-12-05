from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FavoriteBase(BaseModel):
    category: Optional[str] = None
    notes: Optional[str] = None


class FavoriteCreate(FavoriteBase):
    user_id: uuid.UUID
    property_id: uuid.UUID


class FavoriteResponse(FavoriteBase):
    id: uuid.UUID
    user_id: uuid.UUID
    property_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True
