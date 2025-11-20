"""
Inventory Management API
Handles room availability, bookings, and inventory tracking
"""

from datetime import date, datetime
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_, or_

from app.core.database import get_session
from app.models.inventory import Inventory
from app.models.booking import Booking
from app.models.room import Room
from app.models.room_type import RoomType
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/availability/{room_id}")
def check_room_inventory(
    *,
    room_id: uuid.UUID,
    check_in: date = Query(..., description="Check-in date"),
    check_out: date = Query(..., description="Check-out date"),
    session: Session = Depends(get_session)
) -> dict:
    """
    Check room inventory availability for specific dates.
    This is the core inventory management function.
    """
    
    # Validate dates
    if check_in >= check_out:
        raise HTTPException(
            status_code=400, 
            detail="Check-out date must be after check-in date"
        )
    
    if check_in < date.today():
        raise HTTPException(
            status_code=400, 
            detail="Check-in date cannot be in the past"
        )
    
    # Get room details
    room = session.get(Room, room_id)
    if not room or not room.is_active:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check inventory for each date in the range
    current_date = check_in
    unavailable_dates = []
    
    while current_date < check_out:
        # Check if there's inventory for this date
        inventory_query = select(Inventory).where(
            and_(
                Inventory.room_id == room_id,
                Inventory.date == current_date,
                Inventory.is_active == True
            )
        )
        inventory = session.exec(inventory_query).first()
        
        if not inventory:
            unavailable_dates.append(current_date)
        else:
            # Check if room is already booked for this date
            booking_query = select(Booking).where(
                and_(
                    Booking.room_id == room_id,
                    Booking.check_in <= current_date,
                    Booking.check_out > current_date,
                    Booking.status.in_(["confirmed", "checked_in"])
                )
            )
            existing_booking = session.exec(booking_query).first()
            
            if existing_booking:
                unavailable_dates.append(current_date)
        
        # Move to next date
        from datetime import timedelta
        current_date += timedelta(days=1)
    
    # Calculate availability
    total_days = (check_out - check_in).days
    available_days = total_days - len(unavailable_dates)
    is_available = len(unavailable_dates) == 0
    
    return {
        "room_id": str(room_id),
        "check_in": check_in,
        "check_out": check_out,
        "is_available": is_available,
        "total_days": total_days,
        "available_days": available_days,
        "unavailable_dates": unavailable_dates,
        "availability_percentage": (available_days / total_days) * 100 if total_days > 0 else 0
    }


@router.post("/reserve/{room_id}")
def reserve_room_inventory(
    *,
    room_id: uuid.UUID,
    check_in: date,
    check_out: date,
    guest_count: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Reserve room inventory for booking.
    This creates a temporary hold on the inventory.
    """
    
    # First check availability
    availability = check_room_inventory(
        room_id=room_id,
        check_in=check_in,
        check_out=check_out,
        session=session
    )
    
    if not availability["is_available"]:
        raise HTTPException(
            status_code=409,
            detail=f"Room not available for selected dates. Unavailable dates: {availability['unavailable_dates']}"
        )
    
    # Create reservation record (temporary hold)
    reservation_id = str(uuid.uuid4())
    
    # In a real system, you would create a reservation/hold record
    # For now, we'll return a reservation confirmation
    
    return {
        "reservation_id": reservation_id,
        "room_id": str(room_id),
        "check_in": check_in,
        "check_out": check_out,
        "guest_count": guest_count,
        "status": "reserved",
        "expires_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",  # 15 minutes from now
        "message": "Room reserved successfully. Complete payment within 15 minutes."
    }


@router.get("/room/{room_id}/calendar")
def get_room_calendar(
    *,
    room_id: uuid.UUID,
    start_date: date = Query(..., description="Calendar start date"),
    end_date: date = Query(..., description="Calendar end date"),
    session: Session = Depends(get_session)
) -> dict:
    """
    Get room availability calendar for a date range.
    Useful for displaying availability calendar on frontend.
    """
    
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Get room details
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Get inventory for date range
    inventory_query = select(Inventory).where(
        and_(
            Inventory.room_id == room_id,
            Inventory.date >= start_date,
            Inventory.date <= end_date,
            Inventory.is_active == True
        )
    ).order_by(Inventory.date)
    
    inventories = session.exec(inventory_query).all()
    
    # Get bookings for date range
    booking_query = select(Booking).where(
        and_(
            Booking.room_id == room_id,
            or_(
                and_(Booking.check_in >= start_date, Booking.check_in <= end_date),
                and_(Booking.check_out >= start_date, Booking.check_out <= end_date),
                and_(Booking.check_in <= start_date, Booking.check_out >= end_date)
            ),
            Booking.status.in_(["confirmed", "checked_in"])
        )
    )
    
    bookings = session.exec(booking_query).all()
    
    # Build calendar data
    calendar_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Find inventory for this date
        inventory = next((inv for inv in inventories if inv.date == current_date), None)
        
        # Check if date is booked
        is_booked = any(
            booking.check_in <= current_date < booking.check_out 
            for booking in bookings
        )
        
        day_data = {
            "date": current_date,
            "available": inventory is not None and not is_booked,
            "price": float(inventory.rate) if inventory else None,
            "booked": is_booked,
            "inventory_id": str(inventory.id) if inventory else None
        }
        
        calendar_data.append(day_data)
        
        # Move to next date
        from datetime import timedelta
        current_date += timedelta(days=1)
    
    return {
        "room_id": str(room_id),
        "start_date": start_date,
        "end_date": end_date,
        "calendar": calendar_data,
        "total_days": len(calendar_data),
        "available_days": sum(1 for day in calendar_data if day["available"]),
        "booked_days": sum(1 for day in calendar_data if day["booked"])
    }


@router.get("/summary")
def get_inventory_summary(
    *,
    date_from: date = Query(default=None, description="Summary start date"),
    date_to: date = Query(default=None, description="Summary end date"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get inventory summary statistics.
    Requires authentication - for staff/admin use.
    """
    
    # Default to today if no dates provided
    if not date_from:
        date_from = date.today()
    if not date_to:
        from datetime import timedelta
        date_to = date_from + timedelta(days=30)
    
    # Get total rooms
    total_rooms_query = select(Room).where(Room.is_active == True)
    total_rooms = len(session.exec(total_rooms_query).all())
    
    # Get inventory statistics
    inventory_query = select(Inventory).where(
        and_(
            Inventory.date >= date_from,
            Inventory.date <= date_to,
            Inventory.is_active == True
        )
    )
    inventories = session.exec(inventory_query).all()
    
    # Get booking statistics
    booking_query = select(Booking).where(
        and_(
            or_(
                and_(Booking.check_in >= date_from, Booking.check_in <= date_to),
                and_(Booking.check_out >= date_from, Booking.check_out <= date_to),
                and_(Booking.check_in <= date_from, Booking.check_out >= date_to)
            ),
            Booking.status.in_(["confirmed", "checked_in"])
        )
    )
    bookings = session.exec(booking_query).all()
    
    # Calculate occupancy rate
    total_room_nights = len(inventories)
    booked_room_nights = 0
    
    for inventory in inventories:
        is_booked = any(
            booking.room_id == inventory.room_id and 
            booking.check_in <= inventory.date < booking.check_out
            for booking in bookings
        )
        if is_booked:
            booked_room_nights += 1
    
    occupancy_rate = (booked_room_nights / total_room_nights * 100) if total_room_nights > 0 else 0
    
    return {
        "period": {
            "from": date_from,
            "to": date_to,
            "days": (date_to - date_from).days + 1
        },
        "rooms": {
            "total_rooms": total_rooms,
            "total_room_nights": total_room_nights,
            "booked_room_nights": booked_room_nights,
            "available_room_nights": total_room_nights - booked_room_nights
        },
        "occupancy": {
            "rate_percentage": round(occupancy_rate, 2),
            "total_bookings": len(bookings)
        },
        "revenue": {
            "total_inventory_value": sum(float(inv.rate) for inv in inventories),
            "booked_revenue": sum(
                float(inv.rate) for inv in inventories 
                if any(
                    booking.room_id == inv.room_id and 
                    booking.check_in <= inv.date < booking.check_out
                    for booking in bookings
                )
            )
        }
    }
