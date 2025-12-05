from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str = "SYSTEM"


class NotificationCreate(NotificationBase):
    user_id: uuid.UUID
    related_booking_id: Optional[uuid.UUID] = None
    related_property_id: Optional[uuid.UUID] = None


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_read: bool
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        orm_mode = True
