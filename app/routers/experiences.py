"""
Experience Management Router.

This router provides endpoints for managing property experiences - unique activities
and services that guests can enjoy during their stay. Includes CRUD operations
with proper multi-tenant access control.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_
from typing import List, Optional
import uuid

from app.core.database import get_session
from app.models.experience import Experience
from app.models.property import Property
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperienceOut
from app.utils.dependencies import (
    get_active_user, 
    get_organization_context,
    require_manage_properties
)
from app.models.user import User

router = APIRouter(prefix="/experiences", tags=["experiences"])


@router.get("/", response_model=List[ExperienceOut])
def list_experiences(
    session: Session = Depends(get_session),
    property_id: Optional[uuid.UUID] = Query(None, description="Filter by property ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip"),
    current_user: User = Depends(get_active_user)
):
    """
    List experiences with optional filtering.
    
    Public endpoint that shows active experiences, or all experiences
    for authenticated users with proper permissions.
    """
    query = select(Experience)
    
    # Apply filters
    conditions = []
    
    if property_id:
        conditions.append(Experience.property_id == property_id)
    
    if is_active is not None:
        conditions.append(Experience.is_active == is_active)
    elif not current_user or current_user.role == "CUSTOMER":
        # Non-authenticated users and customers only see active experiences
        conditions.append(Experience.is_active == True)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    experiences = session.exec(query).all()
    return experiences


@router.get("/{experience_id}", response_model=ExperienceOut)
def get_experience(
    experience_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Get a specific experience by ID."""
    experience = session.get(Experience, experience_id)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    
    return experience


@router.post("/", response_model=ExperienceOut)
def create_experience(
    experience_data: ExperienceCreate,
    session: Session = Depends(get_session),
    org_context: dict = Depends(get_organization_context),
    _: User = Depends(require_manage_properties())
):
    """
    Create a new experience for a property.
    
    Requires 'can_manage_properties' permission within the organization.
    """
    # Verify the property belongs to the current organization
    property = session.get(Property, experience_data.property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    if property.organization_id != org_context["organization"].id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Property does not belong to your organization"
        )
    
    # Create the experience
    experience = Experience(**experience_data.model_dump())
    session.add(experience)
    session.commit()
    session.refresh(experience)
    
    return experience


@router.put("/{experience_id}", response_model=ExperienceOut)
def update_experience(
    experience_id: uuid.UUID,
    experience_data: ExperienceUpdate,
    session: Session = Depends(get_session),
    org_context: dict = Depends(get_organization_context),
    _: User = Depends(require_manage_properties())
):
    """
    Update an existing experience.
    
    Requires 'can_manage_properties' permission within the organization.
    """
    experience = session.get(Experience, experience_id)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    
    # Verify the property belongs to the current organization
    property = session.get(Property, experience.property_id)
    if not property or property.organization_id != org_context["organization"].id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Experience does not belong to your organization"
        )
    
    # Update the experience
    update_data = experience_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(experience, field, value)
    
    session.add(experience)
    session.commit()
    session.refresh(experience)
    
    return experience


@router.delete("/{experience_id}")
def delete_experience(
    experience_id: uuid.UUID,
    session: Session = Depends(get_session),
    org_context: dict = Depends(get_organization_context),
    _: User = Depends(require_manage_properties())
):
    """
    Delete an experience.
    
    Requires 'can_manage_properties' permission within the organization.
    """
    experience = session.get(Experience, experience_id)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    
    # Verify the property belongs to the current organization
    property = session.get(Property, experience.property_id)
    if not property or property.organization_id != org_context["organization"].id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Experience does not belong to your organization"
        )
    
    session.delete(experience)
    session.commit()
    
    return {"message": "Experience deleted successfully"}


@router.patch("/{experience_id}/toggle-status", response_model=ExperienceOut)
def toggle_experience_status(
    experience_id: uuid.UUID,
    session: Session = Depends(get_session),
    org_context: dict = Depends(get_organization_context),
    _: User = Depends(require_manage_properties())
):
    """
    Toggle the active status of an experience.
    
    Requires 'can_manage_properties' permission within the organization.
    """
    experience = session.get(Experience, experience_id)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    
    # Verify the property belongs to the current organization
    property = session.get(Property, experience.property_id)
    if not property or property.organization_id != org_context["organization"].id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Experience does not belong to your organization"
        )
    
    # Toggle status
    experience.is_active = not experience.is_active
    session.add(experience)
    session.commit()
    session.refresh(experience)
    
    return experience


@router.get("/property/{property_id}", response_model=List[ExperienceOut])
def get_property_experiences(
    property_id: uuid.UUID,
    session: Session = Depends(get_session),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    current_user: Optional[User] = Depends(get_active_user)
):
    """
    Get all experiences for a specific property.
    
    Public endpoint that shows active experiences by default.
    Authenticated users with proper permissions can see all experiences.
    """
    # Verify property exists
    property = session.get(Property, property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    query = select(Experience).where(Experience.property_id == property_id)
    
    # Apply active filter
    if is_active is not None:
        query = query.where(Experience.is_active == is_active)
    elif not current_user or current_user.role == "CUSTOMER":
        # Non-authenticated users and customers only see active experiences
        query = query.where(Experience.is_active == True)
    
    experiences = session.exec(query).all()
    return experiences


@router.get("/search/", response_model=List[ExperienceOut])
def search_experiences(
    session: Session = Depends(get_session),
    q: str = Query(..., description="Search query"),
    property_id: Optional[uuid.UUID] = Query(None, description="Filter by property ID"),
    limit: int = Query(20, description="Maximum number of results"),
    current_user: Optional[User] = Depends(get_active_user)
):
    """
    Search experiences by name or description.
    
    Public endpoint that searches through active experiences.
    """
    query = select(Experience).where(
        and_(
            Experience.is_active == True,
            Experience.name.ilike(f"%{q}%") | Experience.description.ilike(f"%{q}%")
        )
    )
    
    if property_id:
        query = query.where(Experience.property_id == property_id)
    
    query = query.limit(limit)
    
    experiences = session.exec(query).all()
    return experiences
