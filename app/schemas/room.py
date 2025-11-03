from pydantic import BaseModel
from typing import Optional
import uuid

class RoomCreate(BaseModel):
    number: str
    type: str = "standard"
    price_per_night: float
    capacity: int = 2
    description: Optional[str] = None

class RoomOut(BaseModel):
    id: uuid.UUID
    number: str
    type: str
    price_per_night: float
    capacity: int
    description: Optional[str] = None
    is_active: bool
