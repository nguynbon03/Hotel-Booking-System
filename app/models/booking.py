from sqlmodel import SQLModel, Field
from datetime import datetime, date
import uuid
from app.utils.enums import BookingStatus

class Booking(SQLModel, table=True):
    __tablename__ = "bookings"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    room_id: uuid.UUID = Field(foreign_key="rooms.id", index=True)
    check_in: date
    check_out: date
    total_amount: float
    status: str = Field(default=BookingStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
