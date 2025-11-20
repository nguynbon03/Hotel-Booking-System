"""
Enhanced Staff Operations Router.

Comprehensive staff dashboard with customer support, booking management,
property oversight, and performance analytics for hotel staff members.
"""

from __future__ import annotations

import uuid
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_, or_, func

from app.core.database import get_session
from app.utils.dependencies import get_current_staff, get_organization_context
from app.models.booking import Booking
from app.models.user import User
from app.models.property import Property
from app.models.room import Room
from app.models.customer_profile import PropertyReview, CustomerNotification
from app.models.customer_profile import ReviewStatus
from app.models.chat_message import ChatMessage
from app.schemas.booking import BookingOut, BookingUpdate
from app.schemas.customer import PropertyReviewOut
from app.utils.enums import BookingStatus, UserRole

router = APIRouter(prefix="/staff", tags=["staff"])


# ============================================================
# 📊 Staff Dashboard & Analytics
# ============================================================

@router.get("/dashboard")
def get_staff_dashboard(
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context)
):
    """Get comprehensive staff dashboard with key metrics and recent activities."""
    org_id = org_context["organization"].id
    
    # Date ranges
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Booking statistics
    total_bookings = session.exec(
        select(func.count(Booking.id))
        .join(Room, Booking.room_id == Room.id)
        .join(Property, Room.property_id == Property.id)
        .where(Property.organization_id == org_id)
    ).first() or 0
    
    pending_bookings = session.exec(
        select(func.count(Booking.id))
        .join(Room, Booking.room_id == Room.id)
        .join(Property, Room.property_id == Property.id)
        .where(
            and_(
                Property.organization_id == org_id,
                Booking.status == BookingStatus.PENDING
            )
        )
    ).first() or 0
    
    # Today's check-ins and check-outs
    todays_checkins = session.exec(
        select(func.count(Booking.id))
        .join(Room, Booking.room_id == Room.id)
        .join(Property, Room.property_id == Property.id)
        .where(
            and_(
                Property.organization_id == org_id,
                Booking.check_in == today,
                Booking.status == BookingStatus.CONFIRMED
            )
        )
    ).first() or 0
    
    todays_checkouts = session.exec(
        select(func.count(Booking.id))
        .join(Room, Booking.room_id == Room.id)
        .join(Property, Room.property_id == Property.id)
        .where(
            and_(
                Property.organization_id == org_id,
                Booking.check_out == today,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
            )
        )
    ).first() or 0
    
    # Revenue statistics
    monthly_revenue = session.exec(
        select(func.sum(Booking.total_price))
        .join(Room, Booking.room_id == Room.id)
        .join(Property, Room.property_id == Property.id)
        .where(
            and_(
                Property.organization_id == org_id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.created_at >= month_ago
            )
        )
    ).first() or Decimal("0")
    
    # Pending reviews
    pending_reviews = session.exec(
        select(func.count(PropertyReview.id))
        .join(Property, PropertyReview.property_id == Property.id)
        .where(
            and_(
                Property.organization_id == org_id,
                PropertyReview.status == ReviewStatus.PENDING
            )
        )
    ).first() or 0
    
    # Active chat rooms
    active_chats = session.exec(
        select(func.count(ChatMessage.room.distinct()))
        .where(
            and_(
                ChatMessage.room.like("support_%"),
                ChatMessage.created_at >= datetime.utcnow() - timedelta(hours=24)
            )
        )
    ).first() or 0
    
    return {
        "bookings": {
            "total": total_bookings,
            "pending": pending_bookings,
            "todays_checkins": todays_checkins,
            "todays_checkouts": todays_checkouts
        },
        "revenue": {
            "monthly": float(monthly_revenue),
            "currency": "USD"
        },
        "customer_service": {
            "pending_reviews": pending_reviews,
            "active_chats": active_chats
        },
        "organization": {
            "id": str(org_id),
            "name": org_context["organization"].name
        }
    }


# ============================================================
# 📋 Booking Management
# ============================================================

@router.get("/bookings", response_model=List[BookingOut])
def list_all_bookings(
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context),
    status_filter: Optional[str] = Query(None, description="Filter by booking status"),
    check_in_date: Optional[date] = Query(None, description="Filter by check-in date"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """List all bookings for the organization with filtering options."""
    org_id = org_context["organization"].id
    
    query = select(Booking).join(Room, Booking.room_id == Room.id).join(
        Property, Room.property_id == Property.id
    ).where(Property.organization_id == org_id)
    
    # Apply filters
    if status_filter:
        query = query.where(Booking.status == status_filter)
    
    if check_in_date:
        query = query.where(Booking.check_in == check_in_date)
    
    query = query.order_by(Booking.created_at.desc()).offset(offset).limit(limit)
    
    bookings = session.exec(query).all()
    return bookings


@router.patch("/bookings/{booking_id}", response_model=BookingOut)
def modify_booking(
    booking_id: uuid.UUID,
    payload: BookingUpdate,
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context)
):
    """Update a booking (staff/admin only)."""
    org_id = org_context["organization"].id
    
    # Verify booking belongs to organization
    booking = session.exec(
        select(Booking).join(Room, Booking.room_id == Room.id).join(
            Property, Room.property_id == Property.id
        ).where(
            and_(
                Booking.id == booking_id,
                Property.organization_id == org_id
            )
        )
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or doesn't belong to your organization"
        )
    
    # Update booking
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    session.add(booking)
    session.commit()
    session.refresh(booking)
    
    return booking


@router.post("/bookings/{booking_id}/check-in")
def check_in_guest(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context)
):
    """Check in a guest for their booking."""
    org_id = org_context["organization"].id
    
    booking = session.exec(
        select(Booking).join(Room, Booking.room_id == Room.id).join(
            Property, Room.property_id == Property.id
        ).where(
            and_(
                Booking.id == booking_id,
                Property.organization_id == org_id
            )
        )
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only confirmed bookings can be checked in"
        )
    
    # Update booking status
    booking.status = BookingStatus.COMPLETED  # Assuming check-in means active stay
    session.add(booking)
    session.commit()
    
    return {"message": "Guest checked in successfully", "booking_id": str(booking.id)}


@router.post("/bookings/{booking_id}/check-out")
def check_out_guest(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context)
):
    """Check out a guest and complete their booking."""
    org_id = org_context["organization"].id
    
    booking = session.exec(
        select(Booking).join(Room, Booking.room_id == Room.id).join(
            Property, Room.property_id == Property.id
        ).where(
            and_(
                Booking.id == booking_id,
                Property.organization_id == org_id
            )
        )
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Complete the booking
    booking.status = BookingStatus.COMPLETED
    session.add(booking)
    session.commit()
    
    return {"message": "Guest checked out successfully", "booking_id": str(booking.id)}


# ============================================================
# 👥 Customer Management
# ============================================================

@router.get("/customers")
def list_customers(
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context),
    search: Optional[str] = Query(None, description="Search by name or email"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """List customers who have bookings with the organization."""
    org_id = org_context["organization"].id
    
    # Get customers who have bookings with this organization
    query = select(User).join(Booking, User.id == Booking.user_id).join(
        Room, Booking.room_id == Room.id
    ).join(Property, Room.property_id == Property.id).where(
        and_(
            Property.organization_id == org_id,
            User.role == UserRole.CUSTOMER
        )
    ).distinct()
    
    if search:
        query = query.where(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    query = query.offset(offset).limit(limit)
    customers = session.exec(query).all()
    
    # Get additional info for each customer
    customer_data = []
    for customer in customers:
        # Get booking count
        booking_count = session.exec(
            select(func.count(Booking.id))
            .join(Room, Booking.room_id == Room.id)
            .join(Property, Room.property_id == Property.id)
            .where(
                and_(
                    Booking.user_id == customer.id,
                    Property.organization_id == org_id
                )
            )
        ).first() or 0
        
        # Get total spent
        total_spent = session.exec(
            select(func.sum(Booking.total_price))
            .join(Room, Booking.room_id == Room.id)
            .join(Property, Room.property_id == Property.id)
            .where(
                and_(
                    Booking.user_id == customer.id,
                    Property.organization_id == org_id,
                    Booking.status == BookingStatus.COMPLETED
                )
            )
        ).first() or Decimal("0")
        
        customer_data.append({
            "id": str(customer.id),
            "full_name": customer.full_name,
            "email": customer.email,
            "phone": customer.phone,
            "created_at": customer.created_at.isoformat(),
            "booking_count": booking_count,
            "total_spent": float(total_spent),
            "is_active": customer.is_active
        })
    
    return {"customers": customer_data, "total": len(customer_data)}


@router.get("/customers/{customer_id}/bookings")
def get_customer_bookings(
    customer_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context)
):
    """Get all bookings for a specific customer within the organization."""
    org_id = org_context["organization"].id
    
    bookings = session.exec(
        select(Booking).join(Room, Booking.room_id == Room.id).join(
            Property, Room.property_id == Property.id
        ).where(
            and_(
                Booking.user_id == customer_id,
                Property.organization_id == org_id
            )
        ).order_by(Booking.created_at.desc())
    ).all()
    
    return {"bookings": [
        {
            "id": str(booking.id),
            "check_in": booking.check_in.isoformat(),
            "check_out": booking.check_out.isoformat(),
            "status": booking.status,
            "total_price": float(booking.total_price),
            "created_at": booking.created_at.isoformat()
        }
        for booking in bookings
    ]}


# ============================================================
# ⭐ Review Management
# ============================================================

@router.get("/reviews", response_model=List[PropertyReviewOut])
def list_pending_reviews(
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context),
    status_filter: Optional[ReviewStatus] = Query(ReviewStatus.PENDING, description="Filter by review status"),
    limit: int = Query(20, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """List reviews for properties in the organization."""
    org_id = org_context["organization"].id
    
    query = select(PropertyReview).join(
        Property, PropertyReview.property_id == Property.id
    ).where(Property.organization_id == org_id)
    
    if status_filter:
        query = query.where(PropertyReview.status == status_filter)
    
    query = query.order_by(PropertyReview.created_at.desc()).offset(offset).limit(limit)
    
    reviews = session.exec(query).all()
    return reviews


@router.patch("/reviews/{review_id}/moderate")
def moderate_review(
    review_id: uuid.UUID,
    action: str = Query(..., description="Action: approve, reject"),
    notes: Optional[str] = Query(None, description="Moderation notes"),
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context)
):
    """Moderate a review (approve or reject)."""
    org_id = org_context["organization"].id
    
    # Verify review belongs to organization
    review = session.exec(
        select(PropertyReview).join(
            Property, PropertyReview.property_id == Property.id
        ).where(
            and_(
                PropertyReview.id == review_id,
                Property.organization_id == org_id
            )
        )
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Update review status
    if action == "approve":
        review.status = ReviewStatus.APPROVED
    elif action == "reject":
        review.status = ReviewStatus.REJECTED
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Use 'approve' or 'reject'"
        )
    
    review.moderated_by = current_staff.id
    review.moderated_at = datetime.utcnow()
    review.moderation_notes = notes
    
    session.add(review)
    session.commit()
    
    return {"message": f"Review {action}d successfully", "review_id": str(review.id)}


# ============================================================
# 📊 Performance Reports
# ============================================================

@router.get("/reports/daily")
def get_daily_report(
    session: Session = Depends(get_session),
    current_staff: User = Depends(get_current_staff),
    org_context: dict = Depends(get_organization_context),
    report_date: date = Query(default_factory=date.today, description="Date for the report")
):
    """Get daily performance report."""
    org_id = org_context["organization"].id
    
    # Bookings for the day
    daily_bookings = session.exec(
        select(Booking).join(Room, Booking.room_id == Room.id).join(
            Property, Room.property_id == Property.id
        ).where(
            and_(
                Property.organization_id == org_id,
                func.date(Booking.created_at) == report_date
            )
        )
    ).all()
    
    # Check-ins and check-outs
    checkins = [b for b in daily_bookings if b.check_in == report_date]
    checkouts = [b for b in daily_bookings if b.check_out == report_date]
    
    # Revenue
    daily_revenue = sum(b.total_price for b in daily_bookings if b.status == BookingStatus.COMPLETED)
    
    return {
        "date": report_date.isoformat(),
        "bookings": {
            "total": len(daily_bookings),
            "confirmed": len([b for b in daily_bookings if b.status == BookingStatus.CONFIRMED]),
            "pending": len([b for b in daily_bookings if b.status == BookingStatus.PENDING]),
            "cancelled": len([b for b in daily_bookings if b.status == BookingStatus.CANCELLED])
        },
        "checkins": len(checkins),
        "checkouts": len(checkouts),
        "revenue": float(daily_revenue),
        "organization": org_context["organization"].name
    }