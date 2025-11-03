from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    room: str = Field(index=True)
    sender_id: uuid.UUID | None = None  # user/staff id
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
