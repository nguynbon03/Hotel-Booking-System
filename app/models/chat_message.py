from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    room: str = Field(index=True)  # ví dụ: property_123, booking_999
    sender_id: Optional[uuid.UUID] = None   # user_id hoặc staff_id
    content: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
