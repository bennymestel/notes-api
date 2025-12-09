"""
FastAPI application entry point.
Creates the app instance, includes routers, and sets up database tables.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import auth, notes
from app.core.db import Base, engine
from app.models.note import Note  # Import to register model with Base
from app.models.user import User  # Import to register model with Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Creates database tables on startup.
    """
    logger.info("Starting up Notes API")
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield
    # Cleanup on shutdown
    logger.info("Shutting down Notes API")


# Create FastAPI application
app = FastAPI(
    title="Notes API",
    description="A simple REST API for managing notes",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint to verify the API is running."""
    return {"status": "ok"}

