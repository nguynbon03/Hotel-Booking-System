from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.models.booking import Booking
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services.payment_service import charge
from app.services.task_queue import enqueue_invoice
from app.utils.dependencies import get_current_user
from app.utils.enums import PaymentStatus

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentOut)
def pay(payload: PaymentCreate, session: Session = Depends(get_session), current=Depends(get_current_user)):
    booking = session.get(Booking, payload.booking_id)
    if not booking or booking.user_id != current.id:
        raise HTTPException(404, "Booking not found")
    ok, tx = charge(booking.total_amount, payload.method)
    payment = Payment(
        booking_id=booking.id,
        amount=booking.total_amount,
        method=payload.method,
        status=PaymentStatus.SUCCESS if ok else PaymentStatus.FAILED,
        transaction_code=tx,
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)
    # Send invoice email, including the transaction code
    enqueue_invoice(current.email, str(booking.id), booking.total_amount, tx)
    return payment
