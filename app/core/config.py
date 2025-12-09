"""
Configuration settings for the Notes API.
Uses pydantic-settings to load from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database URL - defaults to PostgreSQL in Docker network
    # Use 'postgres' hostname for Docker, override with 'localhost' for local dev
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/notes"
    
    # JWT Authentication
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Demo key - In production, use environment variable with secure key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Notes API"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


# Global settings instance
settings = Settings()

