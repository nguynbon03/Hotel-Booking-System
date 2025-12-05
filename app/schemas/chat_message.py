from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ChatMessageBase(BaseModel):
    room: str
    content: str
    sender_id: Optional[uuid.UUID] = None


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True
