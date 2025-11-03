from sqlmodel import Session, select
from datetime import date
from app.models.booking import Booking
from app.models.room import Room
from app.utils.helpers import nights_between
from app.utils.enums import BookingStatus

def room_available(session: Session, room_id, check_in: date, check_out: date) -> bool:
    q = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
        Booking.check_in <= check_out,
        Booking.check_out >= check_in,
    )
    return session.exec(q).first() is None

def compute_total(room: Room, check_in: date, check_out: date) -> float:
    nights = nights_between(check_in, check_out)
    if nights <= 0:
        raise ValueError("Invalid dates")
    return nights * room.price_per_night
