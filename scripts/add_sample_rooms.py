#!/usr/bin/env python3
"""
Script to add 30 sample rooms with beautiful images to the database.
Run this script to populate the database with realistic hotel room data.
"""

import asyncio
import sys
import os
from decimal import Decimal
from datetime import datetime, date, timedelta
import uuid

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.core.database import engine
from app.models.user import User
from app.models.organization import Organization
from app.models.property import Property
from app.models.room import Room
from app.models.room_type import RoomType
from app.models.rate_plan import RatePlan
from app.models.daily_price import DailyPrice
from app.models.inventory import Inventory

# Beautiful room images from Unsplash
ROOM_IMAGES = [
    "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80",  # Luxury hotel room
    "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80",  # Modern bedroom
    "https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800&q=80",  # Hotel suite
    "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&q=80",  # Elegant room
    "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80",  # Boutique hotel
    "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",  # Luxury suite
    "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&q=80",  # Modern hotel room
    "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=800&q=80",  # Classic room
    "https://images.unsplash.com/photo-1595576508898-0ad5c879a061?w=800&q=80",  # Premium room
    "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800&q=80",  # Executive suite
]

# Sample room data
SAMPLE_ROOMS = [
    # Standard Rooms
    {
        "room_type": "Standard Queen Room",
        "description": "Comfortable queen room with modern amenities and city view. Perfect for business travelers and couples.",
        "capacity": 2,
        "size_sqm": 25,
        "bed_type": "Queen Bed",
        "amenities": ["Free WiFi", "Air Conditioning", "Flat Screen TV", "Mini Fridge", "Coffee Maker", "Work Desk"],
        "base_price": Decimal("120.00"),
        "count": 8
    },
    {
        "room_type": "Standard Twin Room",
        "description": "Spacious twin room ideal for friends or colleagues traveling together. Features two comfortable single beds.",
        "capacity": 2,
        "size_sqm": 28,
        "bed_type": "Twin Beds",
        "amenities": ["Free WiFi", "Air Conditioning", "Flat Screen TV", "Mini Fridge", "Coffee Maker", "Work Desk"],
        "base_price": Decimal("115.00"),
        "count": 6
    },
    
    # Deluxe Rooms
    {
        "room_type": "Deluxe King Room",
        "description": "Luxurious king room with premium furnishings and stunning city skyline views. Includes premium amenities.",
        "capacity": 2,
        "size_sqm": 35,
        "bed_type": "King Bed",
        "amenities": ["Free WiFi", "Air Conditioning", "Smart TV", "Mini Bar", "Nespresso Machine", "Work Desk", "Balcony", "Bathrobes"],
        "base_price": Decimal("180.00"),
        "count": 5
    },
    {
        "room_type": "Deluxe Family Room",
        "description": "Perfect for families with children. Features a king bed and sofa bed, plus family-friendly amenities.",
        "capacity": 4,
        "size_sqm": 40,
        "bed_type": "King Bed + Sofa Bed",
        "amenities": ["Free WiFi", "Air Conditioning", "Smart TV", "Mini Bar", "Coffee Maker", "Microwave", "Family Games", "Extra Towels"],
        "base_price": Decimal("220.00"),
        "count": 4
    },
    
    # Premium Suites
    {
        "room_type": "Executive Suite",
        "description": "Sophisticated suite with separate living area and bedroom. Ideal for extended stays and business meetings.",
        "capacity": 3,
        "size_sqm": 55,
        "bed_type": "King Bed + Sofa",
        "amenities": ["Free WiFi", "Air Conditioning", "Smart TV", "Full Mini Bar", "Nespresso Machine", "Work Desk", "Balcony", "Bathrobes", "Slippers", "Executive Lounge Access"],
        "base_price": Decimal("320.00"),
        "count": 3
    },
    {
        "room_type": "Presidential Suite",
        "description": "Ultimate luxury suite with panoramic city views, separate dining area, and premium amenities throughout.",
        "capacity": 4,
        "size_sqm": 80,
        "bed_type": "King Bed + Living Area",
        "amenities": ["Free WiFi", "Air Conditioning", "Smart TV", "Full Kitchen", "Premium Mini Bar", "Nespresso Machine", "Dining Table", "Balcony", "Bathrobes", "Slippers", "Butler Service", "Airport Transfer"],
        "base_price": Decimal("550.00"),
        "count": 2
    },
    
    # Specialty Rooms
    {
        "room_type": "Accessible Queen Room",
        "description": "Fully accessible room designed for guests with mobility needs. Features wider doorways and accessible bathroom.",
        "capacity": 2,
        "size_sqm": 30,
        "bed_type": "Queen Bed",
        "amenities": ["Free WiFi", "Air Conditioning", "Flat Screen TV", "Mini Fridge", "Coffee Maker", "Accessible Bathroom", "Grab Bars", "Roll-in Shower"],
        "base_price": Decimal("125.00"),
        "count": 2
    }
]

def create_sample_data():
    """Create sample rooms, room types, and related data."""
    with Session(engine) as session:
        print("🏨 Starting to create sample hotel room data...")
        
        # Get or create organization and property
        org = session.exec(select(Organization).limit(1)).first()
        if not org:
            print("❌ No organization found. Please create an organization first.")
            return
            
        property_obj = session.exec(select(Property).where(Property.organization_id == org.id).limit(1)).first()
        if not property_obj:
            # Create a sample property
            property_obj = Property(
                name="Grand Palace Hotel",
                description="Luxury hotel in the heart of the city",
                address="123 Grand Avenue, City Center",
                city="Metropolitan City",
                country="Country",
                phone="+1-555-HOTEL",
                email="info@grandpalacehotel.com",
                organization_id=org.id,
                is_active=True
            )
            session.add(property_obj)
            session.commit()
            session.refresh(property_obj)
            print(f"✅ Created property: {property_obj.name}")
        
        room_counter = 1
        
        for room_data in SAMPLE_ROOMS:
            print(f"\n🏠 Creating {room_data['count']} rooms of type: {room_data['room_type']}")
            
            # Create or get room type
            room_type = session.exec(
                select(RoomType).where(
                    RoomType.name == room_data['room_type'],
                    RoomType.property_id == property_obj.id
                )
            ).first()
            
            if not room_type:
                room_type = RoomType(
                    name=room_data['room_type'],
                    description=room_data['description'],
                    max_occupancy=room_data['capacity'],
                    property_id=property_obj.id,
                    is_active=True
                )
                session.add(room_type)
                session.commit()
                session.refresh(room_type)
                print(f"  ✅ Created room type: {room_type.name}")
            
            # Create individual rooms
            for i in range(room_data['count']):
                room_number = f"{room_counter:03d}"  # 001, 002, etc.
                
                # Check if room already exists
                existing_room = session.exec(
                    select(Room).where(
                        Room.number == room_number,
                        Room.property_id == property_obj.id
                    )
                ).first()
                
                if not existing_room:
                    room = Room(
                        number=room_number,
                        type=room_data['room_type'],
                        room_type_id=room_type.id,
                        property_id=property_obj.id,
                        price_per_night=float(room_data['base_price']),
                        capacity=room_data['capacity'],
                        description=f"Room {room_number} - {room_data['description']}",
                        image_url=ROOM_IMAGES[i % len(ROOM_IMAGES)],  # Cycle through images
                        is_active=True
                    )
                    session.add(room)
                    room_counter += 1
                    
                    # Create rate plan for this room type (only once per room type)
                    existing_rate_plan = session.exec(
                        select(RatePlan).where(
                            RatePlan.room_type_id == room_type.id,
                            RatePlan.property_id == property_obj.id
                        )
                    ).first()
                    
                    if not existing_rate_plan:
                        rate_plan = RatePlan(
                            name=f"Standard Rate - {room_data['room_type']}",
                            property_id=property_obj.id,
                            room_type_id=room_type.id,
                            base_price=float(room_data['base_price']),
                            currency="USD",
                            is_refundable=True,
                            cancellation_policy="Free cancellation up to 24 hours before check-in"
                        )
                        session.add(rate_plan)
                    
            session.commit()
            print(f"  ✅ Created {room_data['count']} rooms")
        
        # Create inventory and daily prices for the next 90 days
        print(f"\n📅 Creating inventory and pricing for the next 90 days...")
        
        room_types = session.exec(select(RoomType).where(RoomType.property_id == property_obj.id)).all()
        rate_plans = session.exec(select(RatePlan).where(RatePlan.property_id == property_obj.id)).all()
        
        start_date = date.today()
        for days_ahead in range(90):
            current_date = start_date + timedelta(days=days_ahead)
            
            for room_type in room_types:
                # Count rooms of this type
                room_count = session.exec(
                    select(Room).where(
                        Room.room_type_id == room_type.id,
                        Room.is_active == True
                    )
                ).all()
                total_rooms = len(room_count)
                
                # Create inventory
                existing_inventory = session.exec(
                    select(Inventory).where(
                        Inventory.room_type_id == room_type.id,
                        Inventory.property_id == property_obj.id,
                        Inventory.date == current_date
                    )
                ).first()
                
                if not existing_inventory:
                    inventory = Inventory(
                        room_type_id=room_type.id,
                        property_id=property_obj.id,
                        date=current_date,
                        total_rooms=total_rooms,
                        booked_rooms=0,
                        closed_for_sale=False
                    )
                    session.add(inventory)
                
                # Create daily prices (with some variation)
                for rate_plan in rate_plans:
                    if rate_plan.room_type_id == room_type.id:
                        existing_price = session.exec(
                            select(DailyPrice).where(
                                DailyPrice.rate_plan_id == rate_plan.id,
                                DailyPrice.date == current_date
                            )
                        ).first()
                        
                        if not existing_price:
                            # Add some price variation (weekend premium, seasonal adjustments)
                            price_multiplier = 1.0
                            
                            # Weekend premium (Friday, Saturday)
                            if current_date.weekday() in [4, 5]:  # Friday, Saturday
                                price_multiplier = 1.2
                            
                            # Holiday season premium (December)
                            if current_date.month == 12:
                                price_multiplier *= 1.15
                            
                            final_price = rate_plan.base_price * price_multiplier
                            
                            daily_price = DailyPrice(
                                rate_plan_id=rate_plan.id,
                                date=current_date,
                                price=final_price,
                                currency="USD"
                            )
                            session.add(daily_price)
        
        session.commit()
        print(f"✅ Created inventory and pricing for 90 days")
        
        # Summary
        total_rooms = session.exec(select(Room).where(Room.property_id == property_obj.id)).all()
        total_room_types = session.exec(select(RoomType).where(RoomType.property_id == property_obj.id)).all()
        
        print(f"\n🎉 Sample data creation completed!")
        print(f"📊 Summary:")
        print(f"   • Property: {property_obj.name}")
        print(f"   • Room Types: {len(total_room_types)}")
        print(f"   • Total Rooms: {len(total_rooms)}")
        print(f"   • Inventory Days: 90 days")
        print(f"   • Price Variations: Weekend & seasonal premiums")
        
        print(f"\n🏨 Room Types Created:")
        for rt in total_room_types:
            room_count = len([r for r in total_rooms if r.room_type_id == rt.id])
            print(f"   • {rt.name}: {room_count} rooms (${rt.base_price}/night)")

if __name__ == "__main__":
    create_sample_data()
