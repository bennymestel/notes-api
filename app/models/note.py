"""
SQLAlchemy model for the Note entity.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.db import Base


def utc_now() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class Note(Base):
    """
    Note model representing a note in the database.
    
    Attributes:
        id: Primary key
        title: Note title (required)
        body: Note content (optional)
        user_id: Foreign key to user who owns this note
        created_at: Timestamp when note was created
        updated_at: Timestamp when note was last updated
        owner: Relationship to User model
    """
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationship to user
    owner = relationship("User", back_populates="notes")

