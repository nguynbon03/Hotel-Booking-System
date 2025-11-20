"""
Search and availability endpoints for hotel booking system.

This router provides endpoints for property search, availability checks,
and pricing information for the SAAS hotel booking platform.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session
from typing import List, Optional, Dict, Any
from datetime import date
import uuid

from app.core.database import get_session
from app.services.search_service import SearchService
from app.utils.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/properties", response_model=Dict[str, Any])
def search_properties(
    city: Optional[str] = Query(None, description="City to search in"),
    check_in: Optional[date] = Query(None, description="Check-in date (YYYY-MM-DD)"),
    check_out: Optional[date] = Query(None, description="Check-out date (YYYY-MM-DD)"),
    guests: int = Query(2, ge=1, le=10, description="Number of guests"),
    property_type: Optional[str] = Query(None, description="Type of property (HOTEL, APARTMENT, etc.)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price per night"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price per night"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization (for multi-tenant)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Search for available properties based on criteria.
    
    This endpoint allows searching for hotels and other properties
    with availability and pricing information.
    """
    
    # Validate date range
    if check_in and check_out:
        if check_in >= check_out:
            raise HTTPException(
                status_code=400, 
                detail="Check-in date must be before check-out date"
            )
        
        # Don't allow bookings too far in the past
        from datetime import date as date_today
        if check_in < date_today.today():
            raise HTTPException(
                status_code=400,
                detail="Check-in date cannot be in the past"
            )
    
    # Validate price range
    if min_price and max_price and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="Minimum price cannot be greater than maximum price"
        )
    
    search_service = SearchService(session)
    
    return search_service.search_properties(
        city=city,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        organization_id=organization_id,
        limit=limit,
        offset=offset
    )


@router.get("/properties/{property_id}", response_model=Dict[str, Any])
def get_property_details(
    property_id: uuid.UUID,
    check_in: Optional[date] = Query(None, description="Check-in date for availability"),
    check_out: Optional[date] = Query(None, description="Check-out date for availability"),
    guests: int = Query(2, ge=1, le=10, description="Number of guests"),
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get detailed information about a specific property.
    
    Includes room types, availability, pricing, and property details.
    """
    
    # Validate date range if provided
    if check_in and check_out:
        if check_in >= check_out:
            raise HTTPException(
                status_code=400,
                detail="Check-in date must be before check-out date"
            )
    
    search_service = SearchService(session)
    
    return search_service.get_property_details(
        property_id=property_id,
        check_in=check_in,
        check_out=check_out,
        guests=guests
    )


@router.get("/availability/{room_type_id}")
def check_room_type_availability(
    room_type_id: uuid.UUID,
    check_in: date = Query(..., description="Check-in date"),
    check_out: date = Query(..., description="Check-out date"),
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Check availability for a specific room type.
    
    Returns the number of available rooms and pricing information.
    """
    
    # Validate date range
    if check_in >= check_out:
        raise HTTPException(
            status_code=400,
            detail="Check-in date must be before check-out date"
        )
    
    search_service = SearchService(session)
    
    # Check if room type exists
    from app.models.room_type import RoomType
    room_type = session.get(RoomType, room_type_id)
    if not room_type or not room_type.is_active:
        raise HTTPException(status_code=404, detail="Room type not found")
    
    # Get availability
    available_count = search_service.get_room_type_availability(
        room_type_id, check_in, check_out
    )
    
    # Get pricing
    pricing = search_service.calculate_room_type_pricing(
        room_type_id, check_in, check_out
    )
    
    return {
        "room_type_id": room_type_id,
        "room_type_name": room_type.name,
        "check_in": check_in,
        "check_out": check_out,
        "available_count": available_count,
        "is_available": available_count > 0,
        "pricing": pricing
    }


@router.get("/cities")
def get_popular_cities(
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """
    Get list of popular cities with available properties.
    
    Useful for autocomplete and city suggestions.
    """
    
    from sqlmodel import select, func
    from app.models.property import Property
    
    # Get cities with property counts
    cities = session.exec(
        select(
            Property.city,
            Property.country,
            func.count(Property.id).label("property_count")
        )
        .where(
            and_(
                Property.is_active == True,
                Property.city.is_not(None),
                Property.city != ""
            )
        )
        .group_by(Property.city, Property.country)
        .order_by(func.count(Property.id).desc())
        .limit(limit)
    ).all()
    
    return [
        {
            "city": city,
            "country": country,
            "property_count": count
        }
        for city, country, count in cities
    ]


@router.get("/property-types")
def get_property_types(
    session: Session = Depends(get_session)
):
    """
    Get list of available property types.
    
    Returns property types with counts for filtering.
    """
    
    from sqlmodel import select, func
    from app.models.property import Property
    
    # Get property types with counts
    types = session.exec(
        select(
            Property.property_type,
            func.count(Property.id).label("count")
        )
        .where(Property.is_active == True)
        .group_by(Property.property_type)
        .order_by(func.count(Property.id).desc())
    ).all()
    
    return [
        {
            "type": prop_type,
            "count": count,
            "display_name": prop_type.replace("_", " ").title()
        }
        for prop_type, count in types
    ]


@router.get("/price-range")
def get_price_range(
    city: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    """
    Get price range for properties to help with filtering.
    
    Returns min and max prices based on current inventory.
    """
    
    from sqlmodel import select, func
    from app.models.rate_plan import RatePlan
    from app.models.room_type import RoomType
    from app.models.property import Property
    
    # Build query for rate plans
    query = select(
        func.min(RatePlan.base_price).label("min_price"),
        func.max(RatePlan.base_price).label("max_price"),
        func.avg(RatePlan.base_price).label("avg_price")
    ).select_from(
        RatePlan.join(RoomType).join(Property)
    ).where(
        Property.is_active == True
    )
    
    # Apply filters
    if city:
        query = query.where(Property.city.ilike(f"%{city}%"))
    
    if property_type:
        query = query.where(Property.property_type == property_type)
    
    result = session.exec(query).first()
    
    if not result or not result[0]:
        return {
            "min_price": 0,
            "max_price": 0,
            "avg_price": 0,
            "currency": "USD"
        }
    
    return {
        "min_price": float(result[0]),
        "max_price": float(result[1]),
        "avg_price": float(result[2]),
        "currency": "USD"  # Could be made dynamic based on property
    }
