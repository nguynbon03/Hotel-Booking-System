"""
Customer Features Router.

Comprehensive customer-facing endpoints including profile management,
reviews, favorites, notifications, and booking preferences.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_, or_, func
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_session
from app.models.user import User
from app.models.customer_profile import (
    CustomerProfile, PropertyReview, CustomerFavorite, 
    BookingPreference, ReviewHelpfulVote, CustomerNotification,
    ReviewStatus
)
from app.models.property import Property
from app.models.booking import Booking
from app.schemas.customer import (
    CustomerProfileCreate, CustomerProfileUpdate, CustomerProfileOut,
    PropertyReviewCreate, PropertyReviewUpdate, PropertyReviewOut,
    CustomerFavoriteCreate, CustomerFavoriteOut,
    CustomerNotificationOut, ReviewHelpfulVoteCreate
)
from app.utils.dependencies import get_active_user, get_current_user_optional
from app.utils.enums import BookingStatus

router = APIRouter(prefix="/customers", tags=["customers"])


# ============================================================
# 👤 Customer Profile Management
# ============================================================

@router.get("/profile", response_model=CustomerProfileOut)
def get_customer_profile(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Get current customer's profile."""
    profile = session.exec(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    ).first()
    
    if not profile:
        # Create default profile if it doesn't exist
        profile = CustomerProfile(user_id=current_user.id)
        session.add(profile)
        session.commit()
        session.refresh(profile)
    
    return profile


@router.post("/profile", response_model=CustomerProfileOut)
def create_customer_profile(
    profile_data: CustomerProfileCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Create or update customer profile."""
    # Check if profile already exists
    existing_profile = session.exec(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT to update."
        )
    
    profile = CustomerProfile(**profile_data.model_dump(), user_id=current_user.id)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    
    return profile


@router.put("/profile", response_model=CustomerProfileOut)
def update_customer_profile(
    profile_data: CustomerProfileUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Update customer profile."""
    profile = session.exec(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    ).first()
    
    if not profile:
        # Create new profile if it doesn't exist
        profile = CustomerProfile(user_id=current_user.id)
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    
    return profile


# ============================================================
# ⭐ Reviews Management
# ============================================================

@router.get("/reviews", response_model=List[PropertyReviewOut])
def get_my_reviews(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    status_filter: Optional[ReviewStatus] = Query(None, description="Filter by review status"),
    limit: int = Query(20, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """Get current customer's reviews."""
    query = select(PropertyReview).where(PropertyReview.user_id == current_user.id)
    
    if status_filter:
        query = query.where(PropertyReview.status == status_filter)
    
    query = query.order_by(PropertyReview.created_at.desc()).offset(offset).limit(limit)
    
    reviews = session.exec(query).all()
    return reviews


@router.post("/reviews", response_model=PropertyReviewOut)
def create_review(
    review_data: PropertyReviewCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Create a new property review."""
    # Verify the property exists
    property = session.get(Property, review_data.property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if booking_id is provided and belongs to the user
    if review_data.booking_id:
        booking = session.get(Booking, review_data.booking_id)
        if not booking or booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Booking not found or doesn't belong to you"
            )
        
        # Check if booking is completed
        if booking.status != BookingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only review completed bookings"
            )
    
    # Check for existing review
    existing_review = session.exec(
        select(PropertyReview).where(
            and_(
                PropertyReview.user_id == current_user.id,
                PropertyReview.property_id == review_data.property_id
            )
        )
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this property"
        )
    
    # Create the review
    review = PropertyReview(**review_data.model_dump(), user_id=current_user.id)
    session.add(review)
    session.commit()
    session.refresh(review)
    
    return review


@router.put("/reviews/{review_id}", response_model=PropertyReviewOut)
def update_review(
    review_id: uuid.UUID,
    review_data: PropertyReviewUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Update an existing review."""
    review = session.get(PropertyReview, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )
    
    # Update fields
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    review.updated_at = datetime.utcnow()
    review.status = ReviewStatus.PENDING  # Reset to pending after update
    
    session.add(review)
    session.commit()
    session.refresh(review)
    
    return review


@router.delete("/reviews/{review_id}")
def delete_review(
    review_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Delete a review."""
    review = session.get(PropertyReview, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    session.delete(review)
    session.commit()
    
    return {"message": "Review deleted successfully"}


@router.post("/reviews/{review_id}/helpful", response_model=dict)
def vote_review_helpful(
    review_id: uuid.UUID,
    vote_data: ReviewHelpfulVoteCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Vote on whether a review is helpful."""
    review = session.get(PropertyReview, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user already voted
    existing_vote = session.exec(
        select(ReviewHelpfulVote).where(
            and_(
                ReviewHelpfulVote.review_id == review_id,
                ReviewHelpfulVote.user_id == current_user.id
            )
        )
    ).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.is_helpful = vote_data.is_helpful
        session.add(existing_vote)
    else:
        # Create new vote
        vote = ReviewHelpfulVote(
            review_id=review_id,
            user_id=current_user.id,
            is_helpful=vote_data.is_helpful
        )
        session.add(vote)
        review.total_votes += 1
    
    # Update helpful votes count
    helpful_count = session.exec(
        select(func.count(ReviewHelpfulVote.id)).where(
            and_(
                ReviewHelpfulVote.review_id == review_id,
                ReviewHelpfulVote.is_helpful == True
            )
        )
    ).first()
    
    review.helpful_votes = helpful_count or 0
    session.add(review)
    session.commit()
    
    return {"message": "Vote recorded successfully", "helpful_votes": review.helpful_votes}


# ============================================================
# ❤️ Favorites Management
# ============================================================

@router.get("/favorites", response_model=List[CustomerFavoriteOut])
def get_favorites(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """Get customer's favorite properties."""
    query = select(CustomerFavorite).where(CustomerFavorite.user_id == current_user.id)
    
    if category:
        query = query.where(CustomerFavorite.category == category)
    
    query = query.order_by(CustomerFavorite.created_at.desc()).offset(offset).limit(limit)
    
    favorites = session.exec(query).all()
    return favorites


@router.post("/favorites", response_model=CustomerFavoriteOut)
def add_favorite(
    favorite_data: CustomerFavoriteCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Add a property to favorites."""
    # Verify the property exists
    property = session.get(Property, favorite_data.property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if already in favorites
    existing_favorite = session.exec(
        select(CustomerFavorite).where(
            and_(
                CustomerFavorite.user_id == current_user.id,
                CustomerFavorite.property_id == favorite_data.property_id
            )
        )
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property is already in your favorites"
        )
    
    favorite = CustomerFavorite(**favorite_data.model_dump(), user_id=current_user.id)
    session.add(favorite)
    session.commit()
    session.refresh(favorite)
    
    return favorite


@router.delete("/favorites/{favorite_id}")
def remove_favorite(
    favorite_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Remove a property from favorites."""
    favorite = session.get(CustomerFavorite, favorite_id)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    if favorite.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only remove your own favorites"
        )
    
    session.delete(favorite)
    session.commit()
    
    return {"message": "Property removed from favorites"}


@router.delete("/favorites/property/{property_id}")
def remove_favorite_by_property(
    property_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Remove a property from favorites by property ID."""
    favorite = session.exec(
        select(CustomerFavorite).where(
            and_(
                CustomerFavorite.user_id == current_user.id,
                CustomerFavorite.property_id == property_id
            )
        )
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found in favorites"
        )
    
    session.delete(favorite)
    session.commit()
    
    return {"message": "Property removed from favorites"}


# ============================================================
# 🔔 Notifications
# ============================================================

@router.get("/notifications", response_model=List[CustomerNotificationOut])
def get_notifications(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    notification_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(20, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip")
):
    """Get customer notifications."""
    query = select(CustomerNotification).where(CustomerNotification.user_id == current_user.id)
    
    if is_read is not None:
        query = query.where(CustomerNotification.is_read == is_read)
    
    if notification_type:
        query = query.where(CustomerNotification.notification_type == notification_type)
    
    # Filter out expired notifications
    query = query.where(
        or_(
            CustomerNotification.expires_at.is_(None),
            CustomerNotification.expires_at > datetime.utcnow()
        )
    )
    
    query = query.order_by(CustomerNotification.created_at.desc()).offset(offset).limit(limit)
    
    notifications = session.exec(query).all()
    return notifications


@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Mark a notification as read."""
    notification = session.get(CustomerNotification, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only mark your own notifications as read"
        )
    
    notification.is_read = True
    session.add(notification)
    session.commit()
    
    return {"message": "Notification marked as read"}


@router.patch("/notifications/mark-all-read")
def mark_all_notifications_read(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Mark all notifications as read."""
    notifications = session.exec(
        select(CustomerNotification).where(
            and_(
                CustomerNotification.user_id == current_user.id,
                CustomerNotification.is_read == False
            )
        )
    ).all()
    
    for notification in notifications:
        notification.is_read = True
        session.add(notification)
    
    session.commit()
    
    return {"message": f"Marked {len(notifications)} notifications as read"}


# ============================================================
# 📊 Customer Statistics
# ============================================================

@router.get("/stats")
def get_customer_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user)
):
    """Get customer statistics and summary."""
    # Get profile
    profile = session.exec(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    ).first()
    
    # Get booking stats
    total_bookings = session.exec(
        select(func.count(Booking.id)).where(Booking.user_id == current_user.id)
    ).first() or 0
    
    completed_bookings = session.exec(
        select(func.count(Booking.id)).where(
            and_(
                Booking.user_id == current_user.id,
                Booking.status == BookingStatus.COMPLETED
            )
        )
    ).first() or 0
    
    total_spent = session.exec(
        select(func.sum(Booking.total_price)).where(
            and_(
                Booking.user_id == current_user.id,
                Booking.status == BookingStatus.COMPLETED
            )
        )
    ).first() or 0
    
    # Get review stats
    total_reviews = session.exec(
        select(func.count(PropertyReview.id)).where(PropertyReview.user_id == current_user.id)
    ).first() or 0
    
    # Get favorites count
    total_favorites = session.exec(
        select(func.count(CustomerFavorite.id)).where(CustomerFavorite.user_id == current_user.id)
    ).first() or 0
    
    # Get unread notifications count
    unread_notifications = session.exec(
        select(func.count(CustomerNotification.id)).where(
            and_(
                CustomerNotification.user_id == current_user.id,
                CustomerNotification.is_read == False
            )
        )
    ).first() or 0
    
    return {
        "profile": {
            "loyalty_points": profile.loyalty_points if profile else 0,
            "loyalty_tier": profile.loyalty_tier if profile else "BRONZE",
            "member_since": current_user.created_at,
        },
        "bookings": {
            "total": total_bookings,
            "completed": completed_bookings,
            "total_spent": float(total_spent),
        },
        "engagement": {
            "reviews_written": total_reviews,
            "favorites_saved": total_favorites,
            "unread_notifications": unread_notifications,
        }
    }
