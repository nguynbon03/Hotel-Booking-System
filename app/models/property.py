from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from app.utils.enums import PropertyType


class Property(SQLModel, table=True):
    __tablename__ = "properties"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organizations.id")

    name: str
    description: Optional[str] = None

    # Địa chỉ đầy đủ
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    # Toạ độ để FE map + search
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Gắn location phân cấp (tỉnh/thành/phường/quận)
    location_id: Optional[uuid.UUID] = Field(default=None, foreign_key="locations.id")
    location_obj: Optional["Location"] = Relationship(back_populates="properties")

    star_rating: Optional[int] = None
    property_type: PropertyType = Field(default=PropertyType.HOTEL)

    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None

    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None

    currency: str = Field(default="USD")

    tax_rate: Optional[float] = None
    service_fee: Optional[float] = None
    cancellation_policy: Optional[str] = None
    house_rules: Optional[str] = None

    main_image_url: Optional[str] = None
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    # RELATIONSHIPS
    organization: "Organization" = Relationship(back_populates="properties")
    images: List["PropertyImage"] = Relationship(back_populates="property")

    room_types: List["RoomType"] = Relationship(back_populates="property")

    # Staff làm tại property
    staff_members: List["User"] = Relationship(back_populates="staff_property")

    amenities: List["Amenity"] = Relationship(
        back_populates="properties",
        link_model="PropertyAmenity"
    )

    reviews: List["PropertyReview"] = Relationship(back_populates="property")
    favorites: List["CustomerFavorite"] = Relationship(back_populates="property")
    experiences: List["Experience"] = Relationship(back_populates="property")


class PropertyImage(SQLModel, table=True):
    __tablename__ = "property_images"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id")

    url: str
    is_main: bool = Field(default=False)

    property: "Property" = Relationship(back_populates="images")
