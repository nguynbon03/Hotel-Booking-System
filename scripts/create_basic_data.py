#!/usr/bin/env python3
"""
Script to create basic data (organization, admin user, property) for the hotel system.
"""

import sys
import os
from datetime import datetime, date
import uuid

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.core.database import engine
from app.models.user import User
from app.models.organization import (
    Organization,
    OrganizationMember,
    SubscriptionPlan,
    OrganizationStatus,
    OrganizationRole,
)
from app.models.property import Property, PropertyImage
from app.utils.security import hash_password
from app.utils.enums import UserRole

def create_basic_data():
    """Create basic organization, admin user, and property."""
    with Session(engine) as session:
        print("🏢 Creating basic hotel system data...")
        
        # Check if organization already exists
        existing_org = session.exec(select(Organization).limit(1)).first()
        if existing_org:
            print(f"✅ Organization already exists: {existing_org.name}")
            return
        
        # Create admin user
        admin_email = "admin@grandpalacehotel.com"
        existing_admin = session.exec(select(User).where(User.email == admin_email)).first()
        
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                full_name="Hotel Administrator",
                phone="+1-555-ADMIN",
                role=UserRole.SUPER_ADMIN,
                password_hash=hash_password("admin123"),
                is_active=True,
                is_verified=True
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            print(f"✅ Created admin user: {admin_user.email}")
        else:
            admin_user = existing_admin
            print(f"✅ Admin user already exists: {admin_user.email}")
        
        # Create organization
        organization = Organization(
            name="Grand Palace Hotel Group",
            slug="grand-palace-hotel",
            description="Luxury hotel chain providing exceptional hospitality services",
            contact_email="info@grandpalacehotel.com",
            contact_phone="+1-555-HOTEL",
            website="https://grandpalacehotel.com",
            address="123 Grand Avenue",
            city="Metropolitan City",
            country="United States",
            subscription_plan=SubscriptionPlan.PROFESSIONAL,
            status=OrganizationStatus.ACTIVE,
            max_properties=10,
            max_users=50,
            max_rooms_per_property=200,
            features_enabled=[
                "booking",
                "analytics",
                "multi_property",
                "staff_management",
                "customer_support",
            ],
            owner_id=admin_user.id,
            is_active=True,
            primary_color="#3B82F6",
            secondary_color="#1E40AF"
        )
        session.add(organization)
        session.commit()
        session.refresh(organization)
        print(f"✅ Created organization: {organization.name}")
        
        # Create organization membership for admin
        org_member = OrganizationMember(
            organization_id=organization.id,
            user_id=admin_user.id,
            role=OrganizationRole.OWNER,
            can_manage_properties=True,
            can_manage_bookings=True,
            can_manage_users=True,
            can_view_analytics=True,
            can_manage_billing=True,
            is_active=True
        )
        session.add(org_member)
        session.commit()
        print(f"✅ Created organization membership for admin")
        
        # Create main property
        image_urls = [
            "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
            "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&q=80",
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80"
        ]

        property_obj = Property(
            name="Grand Palace Hotel",
            description="Luxury hotel in the heart of the city featuring elegant rooms, world-class amenities, and exceptional service",
            address="123 Grand Avenue, City Center",
            city="Metropolitan City",
            state="State",
            country="United States",
            postal_code="12345",
            contact_phone="+1-555-HOTEL",
            contact_email="reservations@grandpalacehotel.com",
            website="https://grandpalacehotel.com",
            organization_id=organization.id,
            check_in_time="15:00",
            check_out_time="11:00",
            currency="USD",
            tax_rate=0.10,
            service_fee=0.05,
            cancellation_policy="Free cancellation up to 24 hours before check-in",
            house_rules="No smoking inside rooms. Pets allowed upon request.",
            main_image_url=image_urls[0],
            is_active=True
        )
        session.add(property_obj)
        session.commit()
        session.refresh(property_obj)

        for idx, url in enumerate(image_urls):
            session.add(
                PropertyImage(
                    property_id=property_obj.id,
                    url=url,
                    is_main=idx == 0,
                )
            )
        session.commit()
        print(f"✅ Created property: {property_obj.name}")
        
        print(f"\n🎉 Basic data creation completed!")
        print(f"📊 Summary:")
        print(f"   • Organization: {organization.name}")
        print(f"   • Admin User: {admin_user.email} (password: admin123)")
        print(f"   • Property: {property_obj.name}")
        print(f"   • Ready for room data creation!")

if __name__ == "__main__":
    create_basic_data()
