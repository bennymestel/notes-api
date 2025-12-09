"""
Pydantic schemas for Note API request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    """Schema for creating a new note."""
    title: str
    body: Optional[str] = None


class NoteUpdate(BaseModel):
    """Schema for updating an existing note. All fields are optional."""
    title: Optional[str] = None
    body: Optional[str] = None


class NoteRead(BaseModel):
    """Schema for reading a note (response model)."""
    id: int
    title: str
    body: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Pydantic v2 configuration to read from ORM models
    model_config = ConfigDict(from_attributes=True)

