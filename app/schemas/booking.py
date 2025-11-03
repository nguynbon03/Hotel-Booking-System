from pydantic import BaseModel
from datetime import date
import uuid

class BookingCreate(BaseModel):
    room_id: uuid.UUID
    check_in: date
    check_out: date

class BookingOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    room_id: uuid.UUID
    check_in: date
    check_out: date
    total_amount: float
    status: str
