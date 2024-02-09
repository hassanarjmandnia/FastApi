from Fast_API.Database.note_db import NoteDatabaseAction
from Fast_API.Note.note_schemas import NoteTableAdd
from Fast_API.Database.models import User, Note
from Fast_API.utils.logger import loggers
from sqlalchemy.orm import Session


class NoteAction:
    def __init__(self, note_database_action):
        self.note_database_action = note_database_action

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
