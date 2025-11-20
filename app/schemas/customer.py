"""
Pydantic schemas for Customer features.

These schemas define the structure for API requests and responses
related to customer profiles, reviews, favorites, and notifications.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid

from app.models.customer_profile import ReviewStatus


# ============================================================
# 👤 Customer Profile Schemas
# ============================================================

class CustomerProfileBase(BaseModel):
    """Base schema for customer profile data."""
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    preferred_currency: str = Field(default="USD")
    preferred_language: str = Field(default="en")
    preferred_room_type: Optional[str] = None
    preferred_bed_type: Optional[str] = None
    preferred_floor: Optional[str] = None
    
    travel_purpose: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    accessibility_needs: Optional[str] = None
    special_requests: Optional[str] = None
    
    email_notifications: bool = Field(default=True)
    sms_notifications: bool = Field(default=False)
    marketing_emails: bool = Field(default=True)


class CustomerProfileCreate(CustomerProfileBase):
    """Schema for creating a customer profile."""
    pass


class CustomerProfileUpdate(BaseModel):
    """Schema for updating a customer profile."""
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    preferred_currency: Optional[str] = None
    preferred_language: Optional[str] = None
    preferred_room_type: Optional[str] = None
    preferred_bed_type: Optional[str] = None
    preferred_floor: Optional[str] = None
    
    travel_purpose: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    accessibility_needs: Optional[str] = None
    special_requests: Optional[str] = None
    
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    marketing_emails: Optional[bool] = None


class CustomerProfileOut(CustomerProfileBase):
    """Schema for customer profile response data."""
    id: uuid.UUID
    user_id: uuid.UUID
    loyalty_points: int
    loyalty_tier: str
    total_bookings: int
    total_spent: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# ⭐ Review Schemas
# ============================================================

class PropertyReviewBase(BaseModel):
    """Base schema for property review data."""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: str = Field(..., max_length=200, description="Review title")
    content: str = Field(..., description="Review content")
    
    cleanliness_rating: Optional[int] = Field(None, ge=1, le=5)
    service_rating: Optional[int] = Field(None, ge=1, le=5)
    location_rating: Optional[int] = Field(None, ge=1, le=5)
    value_rating: Optional[int] = Field(None, ge=1, le=5)
    amenities_rating: Optional[int] = Field(None, ge=1, le=5)


class PropertyReviewCreate(PropertyReviewBase):
    """Schema for creating a property review."""
    property_id: uuid.UUID = Field(..., description="ID of the property being reviewed")
    booking_id: Optional[uuid.UUID] = Field(None, description="ID of the related booking")


class PropertyReviewUpdate(BaseModel):
    """Schema for updating a property review."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    
    cleanliness_rating: Optional[int] = Field(None, ge=1, le=5)
    service_rating: Optional[int] = Field(None, ge=1, le=5)
    location_rating: Optional[int] = Field(None, ge=1, le=5)
    value_rating: Optional[int] = Field(None, ge=1, le=5)
    amenities_rating: Optional[int] = Field(None, ge=1, le=5)


class PropertyReviewOut(PropertyReviewBase):
    """Schema for property review response data."""
    id: uuid.UUID
    user_id: uuid.UUID
    property_id: uuid.UUID
    booking_id: Optional[uuid.UUID]
    
    status: ReviewStatus
    helpful_votes: int
    total_votes: int
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewHelpfulVoteCreate(BaseModel):
    """Schema for voting on review helpfulness."""
    is_helpful: bool = Field(..., description="Whether the review is helpful")


# ============================================================
# ❤️ Favorite Schemas
# ============================================================

class CustomerFavoriteBase(BaseModel):
    """Base schema for customer favorite data."""
    category: Optional[str] = Field(None, description="Category for organization")
    notes: Optional[str] = Field(None, description="Personal notes about the property")


class CustomerFavoriteCreate(CustomerFavoriteBase):
    """Schema for creating a customer favorite."""
    property_id: uuid.UUID = Field(..., description="ID of the property to favorite")


class CustomerFavoriteOut(CustomerFavoriteBase):
    """Schema for customer favorite response data."""
    id: uuid.UUID
    user_id: uuid.UUID
    property_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# 🔔 Notification Schemas
# ============================================================

class CustomerNotificationOut(BaseModel):
    """Schema for customer notification response data."""
    id: uuid.UUID
    title: str
    message: str
    notification_type: str
    
    related_booking_id: Optional[uuid.UUID]
    related_property_id: Optional[uuid.UUID]
    
    is_read: bool
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================
# 📊 Statistics Schemas
# ============================================================

class CustomerStatsOut(BaseModel):
    """Schema for customer statistics response."""
    profile: dict
    bookings: dict
    engagement: dict
