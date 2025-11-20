"""
Simple customer profile models for basic functionality.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PropertyReview(SQLModel, table=True):
    __tablename__ = "property_reviews"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id", index=True)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    rating: int = Field(description="Rating from 1-5")
    comment: Optional[str] = Field(default=None)
    status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerNotification(SQLModel, table=True):
    __tablename__ = "customer_notifications"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str
    message: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerProfile(SQLModel, table=True):
    __tablename__ = "customer_profiles"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    preferences: Optional[str] = None  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerFavorite(SQLModel, table=True):
    __tablename__ = "customer_favorites"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BookingPreference(SQLModel, table=True):
    __tablename__ = "booking_preferences"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    room_type: Optional[str] = None
    bed_type: Optional[str] = None
    smoking_preference: Optional[str] = None
    floor_preference: Optional[str] = None


class ReviewHelpfulVote(SQLModel, table=True):
    __tablename__ = "review_helpful_votes"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    review_id: uuid.UUID = Field(foreign_key="property_reviews.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    is_helpful: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
