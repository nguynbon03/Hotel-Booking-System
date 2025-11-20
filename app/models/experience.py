"""
Simple Experience model for basic functionality.
"""

from __future__ import annotations

import uuid
from typing import Optional
from sqlmodel import SQLModel, Field


class Experience(SQLModel, table=True):
    __tablename__ = "experiences"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    property_id: uuid.UUID = Field(foreign_key="properties.id", index=True)
    name: str = Field(description="Tên của trải nghiệm.")
    description: Optional[str] = Field(default=None, description="Mô tả chi tiết về trải nghiệm.")
    image_url: Optional[str] = Field(default=None, description="Ảnh đại diện cho trải nghiệm.")
    is_active: bool = Field(default=True, description="Đánh dấu trải nghiệm đang hoạt động hay không.")
