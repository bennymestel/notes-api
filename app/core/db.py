"""
Database configuration and session management.
Sets up SQLAlchemy engine, session factory, and provides the get_db dependency.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from app.core.config import settings

# Create SQLAlchemy engine for PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Ensures the session is properly closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

