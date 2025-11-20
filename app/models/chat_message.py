"""
Simple ChatMessage model for basic chat functionality.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from typing import Optional

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    room: str = Field(index=True)
    sender_id: Optional[uuid.UUID] = None  # user/staff id
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
