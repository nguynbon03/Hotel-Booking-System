from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class CustomerNotification(SQLModel, table=True):
    __tablename__ = "customer_notifications"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID = Field(foreign_key="users.id")

    title: str
    message: str
    notification_type: str = Field(default="SYSTEM")

    related_booking_id: Optional[uuid.UUID] = Field(default=None, foreign_key="bookings.id")
    related_property_id: Optional[uuid.UUID] = Field(default=None, foreign_key="properties.id")

    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="notifications")
