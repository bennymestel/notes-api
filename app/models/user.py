"""
SQLAlchemy model for the User entity.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.core.db import Base


def utc_now() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class User(Base):
    """
    User model representing a user in the database.
    
    Attributes:
        id: Primary key
        username: Unique username (required)
        hashed_password: Bcrypt hashed password
        created_at: Timestamp when user was created
        notes: Relationship to user's notes
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    # Relationship to notes
    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")

