"""
CRUD operations for User model.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import UserCreate


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Retrieve a user by username."""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user with hashed password."""
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        username=user_in.username,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password.
    
    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

