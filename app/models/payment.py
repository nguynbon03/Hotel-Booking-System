from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from app.utils.enums import PaymentMethod, PaymentStatus

class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    booking_id: uuid.UUID = Field(foreign_key="bookings.id", index=True)
    amount: float
    method: str = Field(default=PaymentMethod.CARD)
    status: str = Field(default=PaymentStatus.INIT)
    transaction_code: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
