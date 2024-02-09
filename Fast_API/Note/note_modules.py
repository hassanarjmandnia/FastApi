from Fast_API.Database.note_db import NoteDatabaseAction
from Fast_API.Note.note_schemas import NoteTableAdd
from Fast_API.Database.models import User, Note
from Fast_API.utils.logger import loggers
from sqlalchemy.orm import Session
from fastapi import HTTPException, status


class NoteAction:
    def __init__(self, note_database_action):
        self.note_database_action = note_database_action

    async def show_notes(self, db_session: Session):
        notes = self.note_database_action.get_all_of_notes(db_session)
        if not notes:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="Sorry, there are no notes available at the moment. Start adding notes to see them here!",
            )
        return notes

    async def show_note(self, note_id: int, db_session: Session):
        note = self.note_database_action.get_note_by_id(note_id, db_session)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sorry, the note you're looking for does not exist. Please double-check the note ID and try again.",
            )
        return note

    async def add_note(
        self, body_of_note: NoteTableAdd, user: User, db_session: Session
    ):
        new_note = Note(**body_of_note.model_dump(), user_id=user.id)
        new_note = self.note_database_action.add_note(new_note, db_session)
        loggers["info"].info(f"user {user.email} add a note to databse!")
        return new_note


class NoteManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.note_database_action = NoteDatabaseAction()
            cls._instance.worker = NoteAction(cls._instance.note_database_action)
        return cls._instance

    async def add_note(
        self, body_of_note: NoteTableAdd, user: User, db_session: Session
    ):
        return await self.worker.add_note(body_of_note, user, db_session)

    async def show_notes(self, db_session: Session):
        return await self.worker.show_notes(db_session)

    async def show_note(self, note_id: int, db_session: Session):
        return await self.worker.show_note(note_id, db_session)
