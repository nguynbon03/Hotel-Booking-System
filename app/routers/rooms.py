"""
Routes for room management.

This module extends the original room router to provide a more complete
interface for managing rooms.  In addition to listing and creating rooms,
clients can now retrieve individual rooms, update room details and
soft-delete rooms.  The list endpoint supports filtering by price range,
capacity and keywords in the description.  A simple caching mechanism is
maintained for the unfiltered list to reduce load on the database.
"""

from __future__ import annotations

import uuid
from typing import List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.redis import get_cache, set_cache, delete_cache
from app.models.room import Room
from app.models.room_type import RoomType
from app.models.property import Property
from app.models.booking import Booking, BookingStatus
from app.schemas.room import RoomCreate, RoomOut, RoomUpdate
from app.utils.dependencies import get_current_superuser
from app.models.user import User


router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/public/{room_id}")
def get_public_room(
    *,
    room_id: uuid.UUID,
    session: Session = Depends(get_session)
) -> dict:
    """Get a single room by ID for public access."""
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Get property info
    property_info = session.get(Property, room.property_id)
    
    return {
        "id": str(room.id),
        "number": room.number,
        "name": f"Room {room.number}",
        "description": room.description,
        "capacity": room.capacity,
        "price_per_night": float(room.price_per_night),
        "room_type": room.type,
        "amenities": [],  # Room model doesn't have amenities field
        "images": [room.image_url] if room.image_url else [],
        "property": {
            "id": str(property_info.id) if property_info else None,
            "name": property_info.name if property_info else "Unknown Property",
            "location": property_info.location if property_info else "Unknown Location"
        }
    }

@router.get("/public")
def list_public_rooms(
    *,
    session: Session = Depends(get_session),
    limit: Optional[int] = Query(50, description="Số lượng phòng tối đa"),
    offset: Optional[int] = Query(0, description="Vị trí bắt đầu"),
    property_id: Optional[uuid.UUID] = Query(None, description="ID của property"),
    room_type: Optional[str] = Query(None, description="Loại phòng"),
    min_price: Optional[float] = Query(None, description="Giá tối thiểu"),
    max_price: Optional[float] = Query(None, description="Giá tối đa"),
    min_capacity: Optional[int] = Query(None, description="Số người tối thiểu"),
    max_capacity: Optional[int] = Query(None, description="Số người tối đa"),
    amenities: Optional[str] = Query(None, description="Tiện ích (phân cách bằng dấu phẩy)")
) -> dict:
    """
    API công khai để lấy danh sách phòng với thông tin đầy đủ và filters.
    Không cần authentication, phù hợp cho trang public.
    Hỗ trợ pagination và filters theo loại phòng, giá, số người, tiện ích.
    """
    # Base query để lấy rooms với room_type và property info
    query = select(Room, RoomType).join(
        RoomType, Room.room_type_id == RoomType.id
    ).where(
        Room.is_active == True,
        RoomType.is_active == True
    )
    
    # Apply filters
    if property_id:
        query = query.where(RoomType.property_id == property_id)
    
    if room_type:
        query = query.where(Room.type.ilike(f"%{room_type}%"))
    
    if min_price is not None:
        query = query.where(Room.price_per_night >= min_price)
    
    if max_price is not None:
        query = query.where(Room.price_per_night <= max_price)
    
    if min_capacity is not None:
        query = query.where(Room.capacity >= min_capacity)
    
    if max_capacity is not None:
        query = query.where(Room.capacity <= max_capacity)
    
    # Count total for pagination
    count_query = select(Room).join(RoomType, Room.room_type_id == RoomType.id).where(
        Room.is_active == True,
        RoomType.is_active == True
    )
    
    # Apply same filters to count query
    if property_id:
        count_query = count_query.where(RoomType.property_id == property_id)
    if room_type:
        count_query = count_query.where(Room.type.ilike(f"%{room_type}%"))
    if min_price is not None:
        count_query = count_query.where(Room.price_per_night >= min_price)
    if max_price is not None:
        count_query = count_query.where(Room.price_per_night <= max_price)
    if min_capacity is not None:
        count_query = count_query.where(Room.capacity >= min_capacity)
    if max_capacity is not None:
        count_query = count_query.where(Room.capacity <= max_capacity)
    
    total_count = len(session.exec(count_query).all())
    
    # Apply pagination
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    
    results = session.exec(query).all()
    
    rooms_data = []
    for room, room_type in results:
        # Get property info
        property_query = select(Property).where(Property.id == room_type.property_id)
        property_obj = session.exec(property_query).first()
        
        room_data = {
            "id": str(room.id),
            "number": room.number,
            "name": room_type.name,
            "description": room.description or room_type.description,
            "capacity": room.capacity,
            "base_price": float(room.price_per_night),
            "final_price": float(room.price_per_night),  # Có thể tính toán dynamic pricing sau
            "bed_type": getattr(room, 'bed_type', 'Standard Bed'),
            "size_sqm": getattr(room, 'size_sqm', None),
            "amenities": getattr(room, 'amenities', []),
            "image_url": room.image_url,
            "available": True,  # Mặc định available, có thể check availability riêng
            "room_type": {
                "id": str(room_type.id),
                "name": room_type.name,
                "description": room_type.description,
                "max_occupancy": room_type.max_occupancy
            },
            "property": {
                "id": str(property_obj.id) if property_obj else None,
                "name": property_obj.name if property_obj else "Unknown Hotel",
                "city": property_obj.city if property_obj else None,
                "country": property_obj.country if property_obj else None,
                "address": property_obj.address if property_obj else None,
                "rating": property_obj.star_rating if property_obj else 0
            }
        }
        rooms_data.append(room_data)
    
    # Return with pagination info
    return {
        "rooms": rooms_data,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count if limit else False,
            "current_page": (offset // limit) + 1 if limit else 1,
            "total_pages": (total_count + limit - 1) // limit if limit else 1
        },
        "filters_applied": {
            "room_type": room_type,
            "min_price": min_price,
            "max_price": max_price,
            "min_capacity": min_capacity,
            "max_capacity": max_capacity,
            "amenities": amenities
        }
    }


@router.get("", response_model=List[RoomOut])
def list_rooms(
    *,
    session: Session = Depends(get_session),
    min_price: Optional[float] = Query(None, description="Giá thấp nhất cho mỗi đêm"),
    max_price: Optional[float] = Query(None, description="Giá cao nhất cho mỗi đêm"),
    capacity: Optional[int] = Query(None, description="Số người tối thiểu"),
    view: Optional[str] = Query(None, description="Từ khóa mô tả/phong cảnh"),
    room_type: Optional[str] = Query(None, description="Loại phòng (theo tên chuỗi, ví dụ standard, deluxe, suite)"),
    room_type_id: Optional[uuid.UUID] = Query(None, description="ID của RoomType cho phép lọc theo nhóm phòng"),
    property_id: Optional[uuid.UUID] = Query(None, description="ID của property để lọc phòng theo khách sạn"),
) -> List[RoomOut]:
    """Danh sách phòng với hỗ trợ lọc.

    Nếu không truyền bất kỳ tham số lọc nào, kết quả được cache trong 60 giây.
    Các tham số lọc gồm:
      * ``min_price`` và ``max_price``: phạm vi giá mỗi đêm.
      * ``capacity``: số người tối thiểu có thể ở.
      * ``view``: tìm kiếm chuỗi trong mô tả phòng.
      * ``room_type``: loại phòng (standard, deluxe,…).
    """

    # Khi không có filter -> dùng cache
    if not any([min_price, max_price, capacity, view, room_type]):
        cached = get_cache("rooms:all")
        if cached:
            import json
            return [RoomOut(**item) for item in json.loads(cached)]

    # Tạo câu truy vấn động
    query = select(Room).where(Room.is_active == True)  # noqa: E712

    if min_price is not None:
        query = query.where(Room.price_per_night >= min_price)
    if max_price is not None:
        query = query.where(Room.price_per_night <= max_price)
    if capacity is not None:
        query = query.where(Room.capacity >= capacity)
    if view:
        query = query.where(Room.description.ilike(f"%{view}%"))
    if room_type:
        query = query.where(Room.type == room_type)
    if room_type_id:
        query = query.where(Room.room_type_id == room_type_id)
    if property_id:
        query = query.where(Room.property_id == property_id)

    rooms = session.exec(query).all()

    # Lưu cache nếu không có filter
    if not any([min_price, max_price, capacity, view, room_type]):
        import json
        set_cache("rooms:all", json.dumps([r.dict() for r in rooms]), ttl=60)

    return rooms


@router.post("", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
) -> RoomOut:
    """Tạo mới một phòng.

    Chỉ người dùng có vai trò ``ADMIN`` (superuser) mới được phép tạo
    phòng.  Người dùng không có quyền sẽ bị trả về lỗi 403.
    """
    data = payload.model_dump()
    # Nếu có room_type_id, đảm bảo rằng RoomType tồn tại
    rt_id = data.get("room_type_id")
    prop_id = data.get("property_id")
    # If room_type_id is provided, verify it exists and ensure property_id consistency.
    if rt_id is not None:
        rt = session.get(RoomType, rt_id)
        if not rt:
            raise HTTPException(status_code=404, detail="Room type not found")
        # If property_id is not provided, inherit from the room type
        if prop_id is None:
            data["property_id"] = rt.property_id
        # If property_id is provided, ensure it matches the room type's property
        elif prop_id != rt.property_id:
            raise HTTPException(
                status_code=400,
                detail="Property does not match the selected room type",
            )
    # If no room_type_id but property_id is provided, we accept; otherwise property_id may remain None.
    room = Room(**data)
    session.add(room)
    session.commit()
    session.refresh(room)
    # Xoá cache để danh sách được cập nhật
    delete_cache("rooms:all")
    return room


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: uuid.UUID, session: Session = Depends(get_session)) -> RoomOut:
    """Lấy thông tin chi tiết của một phòng."""
    room = session.get(Room, room_id)
    if not room or not room.is_active:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.patch("/{room_id}", response_model=RoomOut)
def update_room(
    *,
    room_id: uuid.UUID,
    payload: RoomUpdate,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
) -> RoomOut:
    """Cập nhật thông tin phòng.

    Chỉ người dùng có vai trò ``ADMIN`` (superuser) mới được phép cập
    nhật phòng.  Các trường không truyền sẽ được giữ nguyên.
    """
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    data = payload.model_dump(exclude_unset=True)
    # Nếu có room_type_id, đảm bảo rằng RoomType tồn tại và phù hợp với property_id
    rt_id = data.get("room_type_id")
    prop_id = data.get("property_id")
    if rt_id is not None:
        rt = session.get(RoomType, rt_id)
        if not rt:
            raise HTTPException(status_code=404, detail="Room type not found")
        # Nếu property_id mới không cung cấp, sử dụng từ room type
        if prop_id is None:
            data["property_id"] = rt.property_id
        # Nếu property_id được cung cấp, phải khớp với room type
        elif prop_id != rt.property_id:
            raise HTTPException(
                status_code=400,
                detail="Property does not match the selected room type",
            )
    # Nếu chỉ property_id được cung cấp mà không có room_type_id, chấp nhận mà không kiểm tra
    for field, value in data.items():
        setattr(room, field, value)

    session.add(room)
    session.commit()
    session.refresh(room)
    # Cập nhật cache
    delete_cache("rooms:all")
    return room


@router.get("/{room_id}/availability")
def check_room_availability(
    *,
    room_id: uuid.UUID,
    check_in: date = Query(..., description="Check-in date"),
    check_out: date = Query(..., description="Check-out date"),
    guests: int = Query(1, description="Number of guests"),
    session: Session = Depends(get_session)
) -> dict:
    """
    Check if a room is available for the specified dates.
    Public endpoint - no authentication required.
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
    
    # Check if room capacity is sufficient
    if guests > room.capacity:
        return {
            "available": False,
            "message": f"Room capacity is {room.capacity}, but {guests} guests requested",
            "room_id": str(room_id),
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests
        }
    
    # Check for conflicting bookings
    conflicting_bookings = session.exec(
        select(Booking).where(
            Booking.room_id == room_id,
            Booking.status.in_([BookingStatus.CONFIRMED]),
            # Check for date overlap: booking overlaps if it starts before check_out and ends after check_in
            Booking.check_in < check_out,
            Booking.check_out > check_in
        )
    ).all()
    
    if conflicting_bookings:
        return {
            "available": False,
            "message": "Room is already booked for the selected dates",
            "room_id": str(room_id),
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "conflicting_bookings": len(conflicting_bookings)
        }
    
    # Calculate nights and pricing using PricingService
    nights = (check_out - check_in).days
    
    from app.services.pricing_service import PricingService
    
    pricing = PricingService.calculate_room_pricing(
        base_price_per_night=float(room.price_per_night),
        nights=nights,
        guests=guests,
        room_capacity=room.capacity,
        check_in=check_in,
        check_out=check_out
    )
    
    # Apply seasonal pricing
    pricing = PricingService.apply_seasonal_pricing(pricing, check_in, check_out)
    
    return {
        "available": True,
        "message": "Room is available for the selected dates",
        "room_id": str(room_id),
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "nights": nights,
        "price_per_night": pricing["base_price_per_night"],
        "total_price": pricing["total_price"],
        "price_breakdown": pricing,
        "room_details": {
            "number": room.number,
            "capacity": room.capacity,
            "description": room.description
        }
    }


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_superuser),
) -> None:
    """Vô hiệu hóa một phòng.

    Chỉ người dùng có vai trò ``ADMIN`` (superuser) mới được phép xóa hoặc
    vô hiệu hóa phòng.  Thay vì xóa cứng khỏi database, chúng ta đặt
    ``is_active=False`` để giữ lại lịch sử.  Nếu cần xóa cứng, thay
    ``session.delete()`` bằng việc cập nhật ``is_active``.
    """
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Soft delete: đánh dấu không hoạt động
    room.is_active = False
    session.add(room)
    session.commit()
    # Xoá cache
    delete_cache("rooms:all")
    return None