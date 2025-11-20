"""
Advanced Analytics and Reporting for SAAS Hotel Booking System.

This router provides comprehensive analytics, reporting, and business intelligence
features for hotel organizations to track performance, revenue, occupancy,
and customer insights.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, and_, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

from app.core.database import get_session
from app.utils.dependencies import (
    get_active_user, 
    require_organization, 
    require_view_analytics,
    get_organization_context
)
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.models.property import Property
from app.models.room import Room
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment
from app.schemas.analytics import (
    RevenueAnalytics,
    OccupancyAnalytics,
    BookingAnalytics,
    CustomerAnalytics,
    PropertyPerformance,
    AnalyticsDateRange,
    RevenueBreakdown,
    TopPerformers,
    AnalyticsSummary
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ============================================================
# 📊 Revenue Analytics
# ============================================================

@router.get("/revenue", response_model=RevenueAnalytics)
def get_revenue_analytics(
    start_date: date = Query(..., description="Start date for analytics"),
    end_date: date = Query(..., description="End date for analytics"),
    property_id: Optional[uuid.UUID] = Query(None, description="Filter by specific property"),
    context: dict = Depends(get_organization_context),
    _: OrganizationMember = Depends(require_view_analytics())
):
    """Get comprehensive revenue analytics for the organization."""
    
    session = context["session"]
    org = context["organization"]
    
    # Base query for bookings in date range
    booking_query = select(Booking).where(
        and_(
            Booking.property_id.in_(
                select(Property.id).where(Property.organization_id == org.id)
            ),
            Booking.created_at >= datetime.combine(start_date, datetime.min.time()),
            Booking.created_at <= datetime.combine(end_date, datetime.max.time())
        )
    )
    
    if property_id:
        booking_query = booking_query.where(Booking.property_id == property_id)
    
    bookings = session.exec(booking_query).all()
    
    # Calculate metrics
    total_revenue = sum(b.total_amount for b in bookings)
    total_bookings = len(bookings)
    confirmed_bookings = [b for b in bookings if b.status == BookingStatus.CONFIRMED]
    cancelled_bookings = [b for b in bookings if b.status == BookingStatus.CANCELLED]
    
    # Revenue by day
    revenue_by_day = {}
    current_date = start_date
    while current_date <= end_date:
        day_bookings = [
            b for b in bookings 
            if b.created_at.date() == current_date
        ]
        revenue_by_day[current_date.isoformat()] = sum(b.total_amount for b in day_bookings)
        current_date += timedelta(days=1)
    
    # Average booking value
    avg_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0
    
    # Growth calculation (compare with previous period)
    previous_start = start_date - (end_date - start_date)
    previous_end = start_date - timedelta(days=1)
    
    previous_bookings = session.exec(
        select(Booking).where(
            and_(
                Booking.property_id.in_(
                    select(Property.id).where(Property.organization_id == org.id)
                ),
                Booking.created_at >= datetime.combine(previous_start, datetime.min.time()),
                Booking.created_at <= datetime.combine(previous_end, datetime.max.time())
            )
        )
    ).all()
    
    previous_revenue = sum(b.total_amount for b in previous_bookings)
    revenue_growth = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
    
    return RevenueAnalytics(
        total_revenue=total_revenue,
        revenue_growth=revenue_growth,
        average_booking_value=avg_booking_value,
        total_bookings=total_bookings,
        confirmed_bookings=len(confirmed_bookings),
        cancelled_bookings=len(cancelled_bookings),
        revenue_by_day=revenue_by_day,
        cancellation_rate=(len(cancelled_bookings) / total_bookings * 100) if total_bookings > 0 else 0
    )


@router.get("/revenue/breakdown", response_model=RevenueBreakdown)
def get_revenue_breakdown(
    start_date: date = Query(...),
    end_date: date = Query(...),
    context: dict = Depends(get_organization_context),
    _: OrganizationMember = Depends(require_view_analytics())
):
    """Get detailed revenue breakdown by property, room type, etc."""
    
    session = context["session"]
    org = context["organization"]
    
    # Revenue by property
    properties = session.exec(
        select(Property).where(Property.organization_id == org.id)
    ).all()
    
    revenue_by_property = {}
    revenue_by_room_type = {}
    
    for prop in properties:
        prop_bookings = session.exec(
            select(Booking).where(
                and_(
                    Booking.property_id == prop.id,
                    Booking.created_at >= datetime.combine(start_date, datetime.min.time()),
                    Booking.created_at <= datetime.combine(end_date, datetime.max.time())
                )
            )
        ).all()
        
        prop_revenue = sum(b.total_amount for b in prop_bookings)
        revenue_by_property[prop.name] = prop_revenue
        
        # Group by room type (simplified - would need room type data)
        for booking in prop_bookings:
            room = session.get(Room, booking.room_id)
            if room:
                room_type = room.type
                revenue_by_room_type[room_type] = revenue_by_room_type.get(room_type, 0) + booking.total_amount
    
    return RevenueBreakdown(
        revenue_by_property=revenue_by_property,
        revenue_by_room_type=revenue_by_room_type,
        revenue_by_month={},  # Would implement monthly breakdown
        revenue_by_source={}   # Would implement booking source tracking
    )


# ============================================================
# 🏨 Occupancy Analytics
# ============================================================

@router.get("/occupancy", response_model=OccupancyAnalytics)
def get_occupancy_analytics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    property_id: Optional[uuid.UUID] = Query(None),
    context: dict = Depends(get_organization_context),
    _: OrganizationMember = Depends(require_view_analytics())
):
    """Get occupancy rate and availability analytics."""
    
    session = context["session"]
    org = context["organization"]
    
    # Get properties
    property_query = select(Property).where(Property.organization_id == org.id)
    if property_id:
        property_query = property_query.where(Property.id == property_id)
    
    properties = session.exec(property_query).all()
    
    # Calculate occupancy metrics
    total_rooms = 0
    total_room_nights = 0
    occupied_room_nights = 0
    occupancy_by_day = {}
    
    for prop in properties:
        # Get rooms for this property
        rooms = session.exec(
            select(Room).where(Room.property_id == prop.id)
        ).all()
        
        property_rooms = len(rooms)
        total_rooms += property_rooms
        
        # Calculate for each day in range
        current_date = start_date
        while current_date <= end_date:
            day_room_nights = property_rooms
            total_room_nights += day_room_nights
            
            # Count occupied rooms for this day
            occupied_rooms = session.exec(
                select(Booking).where(
                    and_(
                        Booking.property_id == prop.id,
                        Booking.check_in <= current_date,
                        Booking.check_out > current_date,
                        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                    )
                )
            ).all()
            
            day_occupied = len(occupied_rooms)
            occupied_room_nights += day_occupied
            
            # Store daily occupancy
            day_key = current_date.isoformat()
            if day_key not in occupancy_by_day:
                occupancy_by_day[day_key] = {"total": 0, "occupied": 0}
            
            occupancy_by_day[day_key]["total"] += day_room_nights
            occupancy_by_day[day_key]["occupied"] += day_occupied
            
            current_date += timedelta(days=1)
    
    # Calculate rates
    overall_occupancy_rate = (occupied_room_nights / total_room_nights * 100) if total_room_nights > 0 else 0
    
    # Convert daily occupancy to percentages
    occupancy_rate_by_day = {}
    for day, data in occupancy_by_day.items():
        rate = (data["occupied"] / data["total"] * 100) if data["total"] > 0 else 0
        occupancy_rate_by_day[day] = rate
    
    return OccupancyAnalytics(
        overall_occupancy_rate=overall_occupancy_rate,
        occupancy_by_day=occupancy_rate_by_day,
        total_rooms=total_rooms,
        average_daily_rate=0,  # Would calculate from pricing data
        revenue_per_available_room=0  # RevPAR calculation
    )


# ============================================================
# 📈 Booking Analytics
# ============================================================

@router.get("/bookings", response_model=BookingAnalytics)
def get_booking_analytics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    context: dict = Depends(get_organization_context),
    _: OrganizationMember = Depends(require_view_analytics())
):
    """Get booking patterns and conversion analytics."""
    
    session = context["session"]
    org = context["organization"]
    
    bookings = session.exec(
        select(Booking).where(
            and_(
                Booking.property_id.in_(
                    select(Property.id).where(Property.organization_id == org.id)
                ),
                Booking.created_at >= datetime.combine(start_date, datetime.min.time()),
                Booking.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        )
    ).all()
    
    # Booking status distribution
    status_distribution = {}
    for status in BookingStatus:
        count = len([b for b in bookings if b.status == status])
        status_distribution[status.value] = count
    
    # Booking patterns by day of week
    bookings_by_weekday = {i: 0 for i in range(7)}  # 0=Monday, 6=Sunday
    for booking in bookings:
        weekday = booking.created_at.weekday()
        bookings_by_weekday[weekday] += 1
    
    # Lead time analysis (days between booking and check-in)
    lead_times = []
    for booking in bookings:
        if booking.check_in:
            lead_time = (booking.check_in - booking.created_at.date()).days
            lead_times.append(lead_time)
    
    average_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0
    
    # Length of stay analysis
    stay_lengths = []
    for booking in bookings:
        if booking.check_in and booking.check_out:
            stay_length = (booking.check_out - booking.check_in).days
            stay_lengths.append(stay_length)
    
    average_stay_length = sum(stay_lengths) / len(stay_lengths) if stay_lengths else 0
    
    return BookingAnalytics(
        total_bookings=len(bookings),
        status_distribution=status_distribution,
        bookings_by_weekday=bookings_by_weekday,
        average_lead_time=average_lead_time,
        average_stay_length=average_stay_length,
        conversion_rate=0,  # Would need to track booking attempts vs completions
        repeat_customer_rate=0  # Would need customer history analysis
    )


# ============================================================
# 👥 Customer Analytics
# ============================================================

@router.get("/customers", response_model=CustomerAnalytics)
def get_customer_analytics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    context: dict = Depends(get_organization_context),
    _: OrganizationMember = Depends(require_view_analytics())
):
    """Get customer behavior and demographics analytics."""
    
    session = context["session"]
    org = context["organization"]
    
    # Get bookings with user information
    bookings_with_users = session.exec(
        select(Booking, User).join(User, Booking.user_id == User.id).where(
            and_(
                Booking.property_id.in_(
                    select(Property.id).where(Property.organization_id == org.id)
                ),
                Booking.created_at >= datetime.combine(start_date, datetime.min.time()),
                Booking.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        )
    ).all()
    
    unique_customers = set()
    customer_bookings = {}
    total_customer_value = {}
    
    for booking, user in bookings_with_users:
        unique_customers.add(user.id)
        
        if user.id not in customer_bookings:
            customer_bookings[user.id] = 0
            total_customer_value[user.id] = 0
        
        customer_bookings[user.id] += 1
        total_customer_value[user.id] += booking.total_amount
    
    # Calculate metrics
    total_customers = len(unique_customers)
    repeat_customers = len([uid for uid, count in customer_bookings.items() if count > 1])
    repeat_customer_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    # Average customer lifetime value
    avg_customer_value = sum(total_customer_value.values()) / total_customers if total_customers > 0 else 0
    
    # Customer segmentation (simplified)
    high_value_customers = len([v for v in total_customer_value.values() if v > avg_customer_value * 2])
    
    return CustomerAnalytics(
        total_customers=total_customers,
        new_customers=0,  # Would need to track first booking dates
        repeat_customers=repeat_customers,
        repeat_customer_rate=repeat_customer_rate,
        average_customer_value=avg_customer_value,
        customer_segments={
            "high_value": high_value_customers,
            "regular": total_customers - high_value_customers - repeat_customers,
            "new": 0
        }
    )


# ============================================================
# 🏆 Top Performers & Summary
# ============================================================

@router.get("/top-performers", response_model=TopPerformers)
def get_top_performers(
    start_date: date = Query(...),
    end_date: date = Query(...),
    context: dict = Depends(get_organization_context),
    _: OrganizationMember = Depends(require_view_analytics())
):
    """Get top performing properties, rooms, and other metrics."""
    
    session = context["session"]
    org = context["organization"]
    
    # Top properties by revenue
    properties = session.exec(
        select(Property).where(Property.organization_id == org.id)
    ).all()
    
    property_performance = []
    for prop in properties:
        bookings = session.exec(
            select(Booking).where(
                and_(
                    Booking.property_id == prop.id,
                    Booking.created_at >= datetime.combine(start_date, datetime.min.time()),
                    Booking.created_at <= datetime.combine(end_date, datetime.max.time())
                )
            )
        ).all()
        
        revenue = sum(b.total_amount for b in bookings)
        booking_count = len(bookings)
        
        property_performance.append({
            "id": str(prop.id),
            "name": prop.name,
            "revenue": revenue,
            "bookings": booking_count
        })
    
    # Sort by revenue
    top_properties = sorted(property_performance, key=lambda x: x["revenue"], reverse=True)[:5]
    
    return TopPerformers(
        top_properties=top_properties,
        top_room_types=[],  # Would implement room type analysis
        top_customers=[],   # Would implement customer ranking
        best_performing_days=[]  # Would implement day-of-week analysis
    )


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    context: dict = Depends(get_organization_context),
    _: OrganizationMember = Depends(require_view_analytics())
):
    """Get high-level analytics summary for dashboard."""
    
    session = context["session"]
    org = context["organization"]
    
    # Get all bookings for the period
    bookings = session.exec(
        select(Booking).where(
            and_(
                Booking.property_id.in_(
                    select(Property.id).where(Property.organization_id == org.id)
                ),
                Booking.created_at >= datetime.combine(start_date, datetime.min.time()),
                Booking.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        )
    ).all()
    
    # Calculate key metrics
    total_revenue = sum(b.total_amount for b in bookings)
    total_bookings = len(bookings)
    confirmed_bookings = len([b for b in bookings if b.status == BookingStatus.CONFIRMED])
    
    # Get property and room counts
    total_properties = session.exec(
        select(func.count(Property.id)).where(Property.organization_id == org.id)
    ).first()
    
    total_rooms = session.exec(
        select(func.count(Room.id)).where(
            Room.property_id.in_(
                select(Property.id).where(Property.organization_id == org.id)
            )
        )
    ).first()
    
    # Calculate growth (simplified)
    revenue_growth = 0  # Would implement period comparison
    booking_growth = 0  # Would implement period comparison
    
    return AnalyticsSummary(
        total_revenue=total_revenue,
        total_bookings=total_bookings,
        total_properties=total_properties or 0,
        total_rooms=total_rooms or 0,
        occupancy_rate=0,  # Would calculate from occupancy analytics
        average_daily_rate=0,  # Would calculate from pricing data
        revenue_growth=revenue_growth,
        booking_growth=booking_growth
    )
