"""
Routes for booking management.

This module expands upon the original booking router to provide full CRUD
functionality.  Users can list their own bookings, view details of a
particular booking, update reservation dates and cancel bookings.  Admin
users may access all bookings.  Business rules ensure that date changes
respect room availability and total costs are recalculated accordingly.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.room import Room
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingUpdate, BookingOut
from app.utils.dependencies import get_current_user
from app.utils.enums import BookingStatus, UserRole
from app.services.booking_service import room_available, compute_total


router = APIRouter(prefix="/bookings", tags=["bookings"])


from pydantic import BaseModel

class GuestBookingRequest(BaseModel):
    room_id: uuid.UUID
    check_in: date
    check_out: date
    guests: int
    guest_name: str
    guest_email: str
    guest_phone: str
    special_requests: Optional[str] = None

@router.post("/public")  # RE-ENABLED for guest bookings with email notifications
def create_guest_booking(
    *,
    session: Session = Depends(get_session),
    booking_request: GuestBookingRequest
) -> dict:
    """
    Create a booking for guest users (no authentication required).
    Public endpoint for the booking flow with email notifications.
    """
    
    # Validate dates
    if booking_request.check_in >= booking_request.check_out:
        raise HTTPException(
            status_code=400, 
            detail="Check-out date must be after check-in date"
        )
    
    if booking_request.check_in < date.today():
        raise HTTPException(
            status_code=400, 
            detail="Check-in date cannot be in the past"
        )
    
    # Get room details
    room = session.get(Room, booking_request.room_id)
    if not room or not room.is_active:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if room capacity is sufficient
    if booking_request.guests > room.capacity:
        raise HTTPException(
            status_code=400,
            detail=f"Room capacity is {room.capacity}, but {booking_request.guests} guests requested"
        )
    
    # Check for conflicting bookings
    from app.models.booking import BookingStatus
    conflicting_bookings = session.exec(
        select(Booking).where(
            Booking.room_id == booking_request.room_id,
            Booking.status.in_([BookingStatus.CONFIRMED]),
            # Check for date overlap
            Booking.check_in < booking_request.check_out,
            Booking.check_out > booking_request.check_in
        )
    ).all()
    
    if conflicting_bookings:
        raise HTTPException(
            status_code=400,
            detail="Room is not available for the selected dates"
        )
    
    # Calculate pricing using PricingService
    nights = (booking_request.check_out - booking_request.check_in).days
    
    from app.services.pricing_service import PricingService
    
    pricing = PricingService.calculate_room_pricing(
        base_price_per_night=float(room.price_per_night),
        nights=nights,
        guests=booking_request.guests,
        room_capacity=room.capacity,
        check_in=booking_request.check_in,
        check_out=booking_request.check_out
    )
    
    # Apply seasonal pricing
    pricing = PricingService.apply_seasonal_pricing(pricing, booking_request.check_in, booking_request.check_out)
    total_price = pricing["total_price"]
    
    # Create booking
    booking = Booking(
        room_id=booking_request.room_id,
        property_id=room.property_id,
        check_in=booking_request.check_in,
        check_out=booking_request.check_out,
        guest_count=booking_request.guests,
        total_amount=total_price,
        status=BookingStatus.PENDING,
        guest_name=booking_request.guest_name,
        guest_email=booking_request.guest_email,
        guest_phone=booking_request.guest_phone,
        special_requests=booking_request.special_requests
    )
    
    session.add(booking)
    session.commit()
    session.refresh(booking)
    
    # Send booking confirmation email asynchronously
    from app.worker.tasks import send_booking_confirmation
    send_booking_confirmation.delay(
        guest_email=booking_request.guest_email,
        guest_name=booking_request.guest_name,
        booking_id=str(booking.id),
        room_number=room.number,
        check_in=str(booking_request.check_in),
        check_out=str(booking_request.check_out),
        guests=booking_request.guests,
        total_amount=total_price,
        special_requests=booking_request.special_requests
    )
    
    return {
        "booking_id": str(booking.id),
        "status": "success",
        "message": "Booking created successfully",
        "booking_details": {
            "room_id": str(booking_request.room_id),
            "check_in": booking_request.check_in,
            "check_out": booking_request.check_out,
            "guests": booking_request.guests,
            "nights": nights,
            "total_price": total_price,
            "guest_name": booking_request.guest_name,
            "guest_email": booking_request.guest_email
        }
    }


@router.get("", response_model=List[BookingOut])
def list_bookings(
    *,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
    status_filter: Optional[str] = None,
) -> List[BookingOut]:
    """Danh sách booking.

    Người dùng thông thường chỉ thấy booking của chính mình, có thể lọc theo
    ``status``.  Nếu người dùng là ADMIN hoặc STAFF, họ có thể thấy toàn bộ
    booking.
    """
    query = select(Booking)
    if current.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.STAFF):
        query = query.where(Booking.user_id == current.id)
    if status_filter:
        query = query.where(Booking.status == status_filter)
    return session.exec(query).all()


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
) -> BookingOut:
    """Xem chi tiết một booking."""
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    # Chỉ cho phép chủ sở hữu hoặc admin/staff truy cập
    if booking.user_id != current.id and current.role not in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
        UserRole.STAFF,
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    return booking


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    *,
    payload: BookingCreate,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
) -> BookingOut:
    """Tạo một booking mới."""
    room = session.get(Room, payload.room_id)
    if not room or not room.is_active:
        raise HTTPException(status_code=404, detail="Room not available")
    if not room_available(session, room.id, payload.check_in, payload.check_out):
        raise HTTPException(status_code=400, detail="Room is not available for selected dates")
    total = compute_total(room, payload.check_in, payload.check_out)
    booking = Booking(
        user_id=current.id,
        room_id=room.id,
        check_in=payload.check_in,
        check_out=payload.check_out,
        total_amount=total,
        status=BookingStatus.CONFIRMED,
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


@router.patch("/{booking_id}", response_model=BookingOut)
def update_booking(
    *,
    booking_id: uuid.UUID,
    payload: BookingUpdate,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
) -> BookingOut:
    """Cập nhật thông tin booking.

    Cho phép điều chỉnh ngày check-in/check-out hoặc cập nhật trạng thái (ví
    dụ "cancelled").  Hệ thống kiểm tra tính khả dụng của phòng khi thay
    đổi ngày và tính lại tổng số tiền.
    """
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    # Chỉ chủ sở hữu hoặc admin/staff được cập nhật
    if booking.user_id != current.id and current.role not in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
        UserRole.STAFF,
    ):
        raise HTTPException(status_code=403, detail="Not authorized to update this booking")

    data = payload.model_dump(exclude_unset=True)

    # Cập nhật trạng thái nếu có
    if "status" in data:
        # Chỉ cho phép các trạng thái xác định trong BookingStatus
        if data["status"] not in (
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
            BookingStatus.CANCELLED,
            BookingStatus.COMPLETED,
        ):
            raise HTTPException(status_code=400, detail="Invalid booking status")
        old_status = booking.status
        booking.status = data["status"]
        
        # Send email when booking is approved
        if old_status == BookingStatus.PENDING and booking.status == BookingStatus.CONFIRMED:
            from app.worker.tasks import send_booking_approved
            room = session.get(Room, booking.room_id)
            send_booking_approved.delay(
                guest_email=booking.guest_email,
                guest_name=booking.guest_name,
                booking_id=str(booking.id),
                room_number=room.number if room else "Unknown",
                check_in=str(booking.check_in),
                check_out=str(booking.check_out)
            )

    # Cập nhật ngày, cần kiểm tra phòng trống và tính lại tổng tiền
    new_check_in = data.get("check_in", booking.check_in)
    new_check_out = data.get("check_out", booking.check_out)
    # Nếu ngày thay đổi, kiểm tra tính hợp lệ và khả dụng
    if new_check_in != booking.check_in or new_check_out != booking.check_out:
        # Validate date order
        if new_check_in >= new_check_out:
            raise HTTPException(status_code=400, detail="check_in must be before check_out")
        # Kiểm tra phòng trống
        if not room_available(session, booking.room_id, new_check_in, new_check_out):
            raise HTTPException(status_code=400, detail="Room is not available for selected dates")
        # Tính lại giá
        room = session.get(Room, booking.room_id)
        total = compute_total(room, new_check_in, new_check_out)
        booking.check_in = new_check_in
        booking.check_out = new_check_out
        booking.total_amount = total

    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
) -> None:
    """Hủy một booking.

    Booking sẽ được chuyển sang trạng thái ``cancelled`` để giữ lịch sử.  Chỉ
    chủ sở hữu hoặc admin/staff có thể hủy.
    """
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current.id and current.role not in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
        UserRole.STAFF,
    ):
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
    booking.status = BookingStatus.CANCELLED
    session.add(booking)
    session.commit()
    return None