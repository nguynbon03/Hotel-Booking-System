from __future__ import annotations
import uuid
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.utils.enums import LocationType


class Location(SQLModel, table=True):
    __tablename__ = "locations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    slug: str = Field(index=True, unique=True)

    type: LocationType = Field(default=LocationType.CITY)
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="locations.id")

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_code: str = Field(default="VN")
    timezone: str = Field(default="Asia/Ho_Chi_Minh")
    is_active: bool = Field(default=True)

    parent: Optional["Location"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Location.id"}
    )
    children: List["Location"] = Relationship(back_populates="parent")

    properties: List["Property"] = Relationship(back_populates="location_obj")
