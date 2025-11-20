"""
Pydantic schemas for Experience model.

These schemas define the structure for API requests and responses
related to property experiences.
"""

from pydantic import BaseModel, Field
from typing import Optional
import uuid


class ExperienceBase(BaseModel):
    """Base schema for experience data."""
    name: str = Field(..., description="Name of the experience")
    description: Optional[str] = Field(None, description="Detailed description of the experience")
    image_url: Optional[str] = Field(None, description="URL of the experience image")
    is_active: bool = Field(True, description="Whether the experience is active")


class ExperienceCreate(ExperienceBase):
    """Schema for creating a new experience."""
    property_id: uuid.UUID = Field(..., description="ID of the property offering this experience")


class ExperienceUpdate(BaseModel):
    """Schema for updating an existing experience."""
    name: Optional[str] = Field(None, description="Name of the experience")
    description: Optional[str] = Field(None, description="Detailed description of the experience")
    image_url: Optional[str] = Field(None, description="URL of the experience image")
    is_active: Optional[bool] = Field(None, description="Whether the experience is active")


class ExperienceOut(ExperienceBase):
    """Schema for experience response data."""
    id: uuid.UUID = Field(..., description="Unique identifier for the experience")
    property_id: uuid.UUID = Field(..., description="ID of the property offering this experience")

    class Config:
        from_attributes = True