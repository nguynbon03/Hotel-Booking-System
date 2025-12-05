from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from app.utils.enums import ReviewStatus


class ReviewBase(BaseModel):
    rating: int
    title: str
    content: str

    cleanliness_rating: Optional[int] = None
    service_rating: Optional[int] = None
    location_rating: Optional[int] = None
    value_rating: Optional[int] = None
    amenities_rating: Optional[int] = None


class ReviewCreate(ReviewBase):
    property_id: uuid.UUID
    user_id: uuid.UUID
    booking_id: Optional[uuid.UUID] = None


class ReviewUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ReviewStatus] = None
    moderation_notes: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: uuid.UUID
    user_id: uuid.UUID
    property_id: uuid.UUID
    booking_id: Optional[uuid.UUID]

    helpful_votes: int
    total_votes: int
    status: ReviewStatus

    moderated_by: Optional[uuid.UUID]
    moderated_at: Optional[datetime]

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ========== Helpful Vote ==========
class HelpfulVoteResponse(BaseModel):
    id: uuid.UUID
    review_id: uuid.UUID
    user_id: uuid.UUID
    is_helpful: bool
    created_at: datetime

    class Config:
        orm_mode = True
