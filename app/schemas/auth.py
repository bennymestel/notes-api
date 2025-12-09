"""
Pydantic schemas for authentication.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for JWT token payload data."""
    username: str | None = None


class UserRead(BaseModel):
    """Schema for reading user information."""
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

