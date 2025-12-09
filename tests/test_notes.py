"""
Integration tests for the Notes API with authentication.
Tests the full CRUD lifecycle: register → login → create → fetch → update → delete.
"""

import pytest
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
from app.models.user import User  # Import to register model with Base
from app.models.note import Note  # Import to register model with Base
from app.api.v1 import auth, notes


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create a test app without the production lifespan
@asynccontextmanager
async def empty_lifespan(app: FastAPI):
    """Empty lifespan that doesn't try to connect to PostgreSQL."""
    yield


# Create test app
app = FastAPI(
    title="Notes API",
    description="A simple REST API for managing notes",
    version="1.0.0",
    lifespan=empty_lifespan,
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])

# Add health check endpoint
@app.get("/health")
def health_check() -> dict:
    """Health check endpoint to verify the API is running."""
    return {"status": "ok"}

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create a test client with a fresh database for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers(client):
    """Create a test user and return authentication headers."""
    # Register a test user
    register_data = {
        "username": "testuser",
        "password": "testpass123",
    }
    client.post("/auth/register", json=register_data)
    
    # Login to get token
    login_data = {
        "username": "testuser",
        "password": "testpass123",
    }
    response = client.post("/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        """Test that health check returns ok status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthentication:
    """Tests for authentication endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        user_data = {
            "username": "newuser",
            "password": "password123",
        }
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password

    def test_register_duplicate_username(self, client):
        """Test that registering with duplicate username fails."""
        user_data = {
            "username": "duplicate",
            "password": "password123",
        }
        # First registration
        client.post("/auth/register", json=user_data)
        
        # Second registration with same username
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_login_success(self, client):
        """Test successful login."""
        # Register user
        user_data = {
            "username": "loginuser",
            "password": "password123",
        }
        client.post("/auth/register", json=user_data)
        
        # Login
        login_data = {
            "username": "loginuser",
            "password": "password123",
        }
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        # Register user
        user_data = {
            "username": "user1",
            "password": "correctpass",
        }
        client.post("/auth/register", json=user_data)
        
        # Login with wrong password
        login_data = {
            "username": "user1",
            "password": "wrongpass",
        }
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "password123",
        }
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401


class TestNotesAPI:
    """Tests for the Notes CRUD endpoints with authentication."""

    def test_create_note_without_auth(self, client):
        """Test that creating a note without authentication fails."""
        note_data = {"title": "Test Note"}
        response = client.post("/notes/", json=note_data)
        
        assert response.status_code == 401

    def test_create_note(self, client, auth_headers):
        """Test creating a new note with authentication."""
        note_data = {
            "title": "Test Note",
            "body": "This is a test note body",
        }
        response = client.post("/notes/", json=note_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == note_data["title"]
        assert data["body"] == note_data["body"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_note_minimal(self, client, auth_headers):
        """Test creating a note with only required fields."""
        note_data = {"title": "Minimal Note"}
        response = client.post("/notes/", json=note_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Note"
        assert data["body"] is None

    def test_get_notes_empty(self, client, auth_headers):
        """Test getting notes when none exist."""
        response = client.get("/notes/", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_notes(self, client, auth_headers):
        """Test getting all notes."""
        # Create two notes
        client.post("/notes/", json={"title": "Note 1"}, headers=auth_headers)
        client.post("/notes/", json={"title": "Note 2"}, headers=auth_headers)
        
        response = client.get("/notes/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_user_isolation(self, client):
        """Test that users can only see their own notes."""
        # Create first user and note
        user1_data = {"username": "user1", "password": "password1"}
        client.post("/auth/register", json=user1_data)
        login1 = client.post("/auth/login", json=user1_data)
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        client.post("/notes/", json={"title": "User 1 Note"}, headers=headers1)
        
        # Create second user and note
        user2_data = {"username": "user2", "password": "password2"}
        client.post("/auth/register", json=user2_data)
        login2 = client.post("/auth/login", json=user2_data)
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        client.post("/notes/", json={"title": "User 2 Note"}, headers=headers2)
        
        # User 1 should only see their note
        response1 = client.get("/notes/", headers=headers1)
        notes1 = response1.json()
        assert len(notes1) == 1
        assert notes1[0]["title"] == "User 1 Note"
        
        # User 2 should only see their note
        response2 = client.get("/notes/", headers=headers2)
        notes2 = response2.json()
        assert len(notes2) == 1
        assert notes2[0]["title"] == "User 2 Note"

    def test_get_note_by_id(self, client, auth_headers):
        """Test getting a single note by ID."""
        # Create a note
        create_response = client.post("/notes/", json={"title": "Get Me"}, headers=auth_headers)
        note_id = create_response.json()["id"]
        
        response = client.get(f"/notes/{note_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json()["title"] == "Get Me"

    def test_get_note_not_found(self, client, auth_headers):
        """Test getting a non-existent note returns 404."""
        response = client.get("/notes/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_update_note(self, client, auth_headers):
        """Test updating an existing note."""
        # Create a note
        create_response = client.post("/notes/", json={"title": "Original Title"}, headers=auth_headers)
        note_id = create_response.json()["id"]
        
        # Update the note
        update_data = {"title": "Updated Title", "body": "New body content"}
        response = client.put(f"/notes/{note_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["body"] == "New body content"

    def test_update_note_partial(self, client, auth_headers):
        """Test partial update of a note."""
        # Create a note with body
        create_response = client.post(
            "/notes/",
            json={"title": "Original", "body": "Original body"},
            headers=auth_headers,
        )
        note_id = create_response.json()["id"]
        
        # Update only the title
        response = client.put(f"/notes/{note_id}", json={"title": "New Title"}, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["body"] == "Original body"  # Body should remain unchanged

    def test_update_note_not_found(self, client, auth_headers):
        """Test updating a non-existent note returns 404."""
        response = client.put("/notes/999", json={"title": "Updated"}, headers=auth_headers)
        
        assert response.status_code == 404

    def test_delete_note(self, client, auth_headers):
        """Test deleting a note."""
        # Create a note
        create_response = client.post("/notes/", json={"title": "Delete Me"}, headers=auth_headers)
        note_id = create_response.json()["id"]
        
        # Delete the note
        response = client.delete(f"/notes/{note_id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify the note is deleted
        get_response = client.get(f"/notes/{note_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_note_not_found(self, client, auth_headers):
        """Test deleting a non-existent note returns 404."""
        response = client.delete("/notes/999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_full_crud_lifecycle(self, client, auth_headers):
        """Test the complete CRUD lifecycle: create → fetch → update → delete."""
        # CREATE
        create_data = {"title": "Lifecycle Note", "body": "Initial body"}
        create_response = client.post("/notes/", json=create_data, headers=auth_headers)
        assert create_response.status_code == 201
        note_id = create_response.json()["id"]
        
        # READ
        get_response = client.get(f"/notes/{note_id}", headers=auth_headers)
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Lifecycle Note"
        
        # UPDATE
        update_response = client.put(
            f"/notes/{note_id}",
            json={"title": "Updated Lifecycle Note", "body": "Updated body"},
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Lifecycle Note"
        
        # DELETE
        delete_response = client.delete(f"/notes/{note_id}", headers=auth_headers)
        assert delete_response.status_code == 204
        
        # VERIFY DELETED
        verify_response = client.get(f"/notes/{note_id}", headers=auth_headers)
        assert verify_response.status_code == 404
