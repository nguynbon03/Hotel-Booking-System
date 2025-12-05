from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship

from app.utils.enums import ReviewStatus


class PropertyReview(SQLModel, table=True):
    __tablename__ = "property_reviews"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID = Field(foreign_key="users.id")
    property_id: uuid.UUID = Field(foreign_key="properties.id")
    booking_id: Optional[uuid.UUID] = Field(default=None, foreign_key="bookings.id")

    rating: int
    title: str
    content: str

    cleanliness_rating: Optional[int] = None
    service_rating: Optional[int] = None
    location_rating: Optional[int] = None
    value_rating: Optional[int] = None
    amenities_rating: Optional[int] = None

    status: ReviewStatus = Field(default=ReviewStatus.PENDING)

    helpful_votes: int = Field(default=0)
    total_votes: int = Field(default=0)

    moderated_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    moderated_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="customer_reviews")
    property: "Property" = Relationship(back_populates="reviews")
    votes: List["ReviewHelpfulVote"] = Relationship(back_populates="review")


class ReviewHelpfulVote(SQLModel, table=True):
    __tablename__ = "review_helpful_votes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    review_id: uuid.UUID = Field(foreign_key="property_reviews.id")
    user_id: uuid.UUID = Field(foreign_key="users.id")

    is_helpful: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    review: "PropertyReview" = Relationship(back_populates="votes")
