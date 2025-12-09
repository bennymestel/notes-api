"""
CRUD operations for Note model.
Provides database access functions used by the API layer.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate

logger = logging.getLogger(__name__)


def get_note(db: Session, note_id: int, user_id: int) -> Optional[Note]:
    """Retrieve a single note by ID for a specific user."""
    return db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()


def get_notes(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Note]:
    """Retrieve all notes for a specific user with optional pagination."""
    return db.query(Note).filter(Note.user_id == user_id).offset(skip).limit(limit).all()


def create_note(db: Session, note_in: NoteCreate, user_id: int) -> Note:
    """Create a new note for a specific user."""
    db_note = Note(
        title=note_in.title,
        body=note_in.body,
        user_id=user_id,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    logger.info(f"Note created id={db_note.id} user_id={user_id} title='{db_note.title}'")
    return db_note


def update_note(db: Session, note: Note, note_in: NoteUpdate) -> Note:
    """Update an existing note with provided fields."""
    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    logger.info(f"Note updated id={note.id} fields={list(update_data.keys())}")
    return note


def delete_note(db: Session, note: Note) -> None:
    """Delete a note from the database."""
    note_id = note.id
    db.delete(note)
    db.commit()
    logger.info(f"Note deleted id={note_id}")

