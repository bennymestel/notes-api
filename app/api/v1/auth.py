"""
Authentication endpoints for user registration and login.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import create_access_token
from app.crud import user as crud_user
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """
    Register a new user.
    
    Args:
        user_in: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username already exists
    """
    # Check if username already exists
    existing_user = crud_user.get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Create new user
    user = crud_user.create_user(db=db, user_in=user_in)
    logger.info(f"User registered username={user.username}")
    return user


@router.post("/login", response_model=Token)
def login(
    user_login: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    """
    Login and get JWT access token.
    
    Args:
        user_login: Login credentials (username and password)
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = crud_user.authenticate_user(db, username=user_login.username, password=user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    
    logger.info(f"User logged in username={user.username}")
    return Token(access_token=access_token, token_type="bearer")

