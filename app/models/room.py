from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Room(SQLModel, table=True):
    __tablename__ = "rooms"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    number: str = Field(index=True, nullable=False)
    type: str = Field(default="standard")
    price_per_night: float = Field(gt=0)
    capacity: int = Field(default=2, ge=1)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
