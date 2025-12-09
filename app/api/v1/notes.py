"""
API endpoints for Notes.
Provides RESTful CRUD operations for managing notes.
All endpoints require authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.crud import note as crud_note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteRead

router = APIRouter()


@router.post("/", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteRead:
    """Create a new note for the authenticated user."""
    return crud_note.create_note(db=db, note_in=note_in, user_id=current_user.id)


@router.get("/", response_model=list[NoteRead])
def read_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NoteRead]:
    """Retrieve all notes for the authenticated user with optional pagination."""
    return crud_note.get_notes(db=db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{note_id}", response_model=NoteRead)
def read_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteRead:
    """Retrieve a single note by ID for the authenticated user."""
    note = crud_note.get_note(db=db, note_id=note_id, user_id=current_user.id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    return note


@router.put("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: int,
    note_in: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteRead:
    """Update an existing note for the authenticated user."""
    note = crud_note.get_note(db=db, note_id=note_id, user_id=current_user.id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    return crud_note.update_note(db=db, note=note, note_in=note_in)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a note for the authenticated user."""
    note = crud_note.get_note(db=db, note_id=note_id, user_id=current_user.id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    crud_note.delete_note(db=db, note=note)

