"""
Pydantic schemas for Chat system.

These schemas define the structure for API requests and responses
related to real-time chat functionality.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ChatMessageBase(BaseModel):
    """Base schema for chat message data."""
    content: str = Field(..., description="Message content")


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message."""
    room: str = Field(..., description="Chat room identifier")
    sender_id: Optional[uuid.UUID] = Field(None, description="ID of the message sender")


class ChatMessageOut(ChatMessageBase):
    """Schema for chat message response data."""
    id: uuid.UUID
    room: str
    sender_id: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRoomOut(BaseModel):
    """Schema for chat room information."""
    room: str = Field(..., description="Room identifier")
    room_type: str = Field(..., description="Type of room (support, property, booking, general)")
    context_id: Optional[uuid.UUID] = Field(None, description="Related context ID (property, booking, etc.)")
    last_message: Optional[str] = Field(None, description="Last message in the room")
    last_message_at: Optional[datetime] = Field(None, description="Timestamp of last message")
    unread_count: int = Field(0, description="Number of unread messages")

    class Config:
        from_attributes = True