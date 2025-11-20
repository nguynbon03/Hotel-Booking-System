"""
Enhanced AI Recommendation Router.

Provides intelligent recommendations for rooms, properties, and experiences
using advanced machine learning algorithms and user preference analysis.
"""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional, List
from datetime import date
import uuid

from app.core.database import get_session
from app.schemas.ai import RecommendIn
from app.services.ai_recommend import recommend_rooms, AIRecommendationEngine
from app.utils.dependencies import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/recommend")
def recommend_legacy(payload: RecommendIn, session: Session = Depends(get_session)):
    """Legacy recommendation endpoint for backward compatibility."""
    rooms = recommend_rooms(session, payload.view, payload.price_max, payload.capacity)
    return {"result": [r.dict() for r in rooms]}


@router.get("/recommendations/rooms")
def get_room_recommendations(
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional),
    view: Optional[str] = Query(None, description="Preferred view (ocean, mountain, city, etc.)"),
    price_max: Optional[float] = Query(None, description="Maximum price per night"),
    capacity: Optional[int] = Query(None, description="Minimum room capacity"),
    check_in: Optional[date] = Query(None, description="Check-in date"),
    check_out: Optional[date] = Query(None, description="Check-out date"),
    city: Optional[str] = Query(None, description="Preferred city"),
    amenities: Optional[str] = Query(None, description="Comma-separated list of required amenities"),
    limit: int = Query(10, description="Maximum number of recommendations")
):
    """
    Get intelligent room recommendations based on user preferences and history.
    
    This endpoint provides personalized room recommendations using advanced AI algorithms
    that consider user booking history, preferences, and real-time availability.
    """
    engine = AIRecommendationEngine(session)
    
    # Parse amenities
    amenities_list = amenities.split(",") if amenities else None
    
    recommendations = engine.recommend_rooms(
        user_id=current_user.id if current_user else None,
        view=view,
        price_max=price_max,
        capacity=capacity,
        check_in=check_in,
        check_out=check_out,
        city=city,
        amenities=amenities_list,
        limit=limit
    )
    
    return {
        "recommendations": recommendations,
        "personalized": current_user is not None,
        "total": len(recommendations)
    }


@router.get("/recommendations/properties")
def get_property_recommendations(
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional),
    city: Optional[str] = Query(None, description="Preferred city"),
    price_min: Optional[float] = Query(None, description="Minimum price range"),
    price_max: Optional[float] = Query(None, description="Maximum price range"),
    rating_min: Optional[float] = Query(None, description="Minimum rating"),
    amenities: Optional[str] = Query(None, description="Comma-separated list of required amenities"),
    limit: int = Query(10, description="Maximum number of recommendations")
):
    """
    Get intelligent property recommendations based on user preferences.
    
    This endpoint provides personalized property recommendations considering
    user history, ratings, and specified criteria.
    """
    engine = AIRecommendationEngine(session)
    
    # Parse price range
    price_range = None
    if price_min is not None or price_max is not None:
        price_range = (price_min or 0, price_max or float('inf'))
    
    # Parse amenities
    amenities_list = amenities.split(",") if amenities else None
    
    recommendations = engine.recommend_properties(
        user_id=current_user.id if current_user else None,
        city=city,
        price_range=price_range,
        rating_min=rating_min,
        amenities=amenities_list,
        limit=limit
    )
    
    return {
        "recommendations": recommendations,
        "personalized": current_user is not None,
        "total": len(recommendations)
    }


@router.get("/recommendations/experiences")
def get_experience_recommendations(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_optional),
    property_id: Optional[uuid.UUID] = Query(None, description="Filter by specific property"),
    limit: int = Query(5, description="Maximum number of recommendations")
):
    """
    Get personalized experience recommendations.
    
    Requires authentication to provide personalized recommendations based on
    user preferences and booking history.
    """
    if not current_user:
        return {
            "error": "Authentication required for personalized experience recommendations",
            "recommendations": [],
            "personalized": False,
            "total": 0
        }
    
    engine = AIRecommendationEngine(session)
    
    recommendations = engine.get_personalized_experiences(
        user_id=current_user.id,
        property_id=property_id,
        limit=limit
    )
    
    return {
        "recommendations": recommendations,
        "personalized": True,
        "total": len(recommendations)
    }


@router.get("/user/preferences")
def get_user_preferences(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get user's extracted preferences based on booking history.
    
    This endpoint analyzes the user's booking history to extract preferences
    for cities, price ranges, amenities, and room types.
    """
    if not current_user:
        return {
            "error": "Authentication required to view preferences",
            "preferences": None
        }
    
    engine = AIRecommendationEngine(session)
    preferences = engine._get_user_preferences(current_user.id)
    
    return {
        "preferences": preferences,
        "user_id": str(current_user.id)
    }


@router.post("/recommendations/smart-search")
def smart_search(
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional),
    query: str = Query(..., description="Natural language search query"),
    limit: int = Query(10, description="Maximum number of results")
):
    """
    Smart search using natural language processing.
    
    This endpoint accepts natural language queries and returns intelligent
    recommendations based on the query content and user preferences.
    
    Example queries:
    - "Luxury hotel with ocean view in Miami under $300"
    - "Family-friendly resort with pool and spa"
    - "Business hotel near downtown with meeting rooms"
    """
    # Simple keyword extraction (can be enhanced with NLP libraries)
    query_lower = query.lower()
    
    # Extract parameters from query
    view = None
    if any(word in query_lower for word in ['ocean', 'sea', 'beach']):
        view = 'ocean'
    elif any(word in query_lower for word in ['mountain', 'hill']):
        view = 'mountain'
    elif any(word in query_lower for word in ['city', 'downtown', 'urban']):
        view = 'city'
    
    # Extract price hints
    price_max = None
    if 'under' in query_lower:
        # Simple price extraction
        words = query_lower.split()
        for i, word in enumerate(words):
            if word == 'under' and i + 1 < len(words):
                try:
                    price_max = float(words[i + 1].replace('$', '').replace(',', ''))
                except ValueError:
                    pass
    
    # Extract capacity hints
    capacity = None
    if any(word in query_lower for word in ['family', 'group']):
        capacity = 4
    elif any(word in query_lower for word in ['couple', 'romantic']):
        capacity = 2
    
    # Extract city
    city = None
    common_cities = ['miami', 'new york', 'los angeles', 'chicago', 'houston', 'phoenix']
    for city_name in common_cities:
        if city_name in query_lower:
            city = city_name.title()
            break
    
    # Extract amenities
    amenities = []
    amenity_keywords = {
        'pool': 'pool',
        'spa': 'spa',
        'gym': 'fitness center',
        'fitness': 'fitness center',
        'wifi': 'wifi',
        'parking': 'parking',
        'restaurant': 'restaurant',
        'bar': 'bar',
        'meeting': 'meeting rooms',
        'business': 'business center'
    }
    
    for keyword, amenity in amenity_keywords.items():
        if keyword in query_lower:
            amenities.append(amenity)
    
    # Get recommendations using extracted parameters
    engine = AIRecommendationEngine(session)
    
    recommendations = engine.recommend_rooms(
        user_id=current_user.id if current_user else None,
        view=view,
        price_max=price_max,
        capacity=capacity,
        city=city,
        amenities=amenities if amenities else None,
        limit=limit
    )
    
    return {
        "query": query,
        "extracted_parameters": {
            "view": view,
            "price_max": price_max,
            "capacity": capacity,
            "city": city,
            "amenities": amenities
        },
        "recommendations": recommendations,
        "personalized": current_user is not None,
        "total": len(recommendations)
    }
