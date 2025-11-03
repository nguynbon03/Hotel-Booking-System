from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.models.room import Room
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingOut
from app.utils.dependencies import get_current_user
from app.services.booking_service import room_available, compute_total
from app.utils.enums import BookingStatus

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("", response_model=BookingOut)
def create_booking(payload: BookingCreate, session: Session = Depends(get_session), current=Depends(get_current_user)):
    room = session.get(Room, payload.room_id)
    if not room or not room.is_active:
        raise HTTPException(404, "Room not available")
    if not room_available(session, room.id, payload.check_in, payload.check_out):
        raise HTTPException(400, "Room is not available for selected dates")
    total = compute_total(room, payload.check_in, payload.check_out)
    booking = Booking(user_id=current.id, room_id=room.id, check_in=payload.check_in, check_out=payload.check_out,
                      total_amount=total, status=BookingStatus.CONFIRMED)
    session.add(booking); session.commit(); session.refresh(booking)
    return booking
