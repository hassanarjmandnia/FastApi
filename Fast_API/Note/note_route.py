from Fast_API.Database.database import DatabaseManager
from Fast_API.User.user_modules import UserManager
from Fast_API.utils.logger import loggers
from Fast_API.Database.models import User
from fastapi import APIRouter, Depends
from .note_schemas import NoteTableAdd
from .note_modules import NoteManager
from sqlalchemy.orm import Session

note_router = APIRouter()


@note_router.post("/add_note")
async def add_note(
    body_of_note: NoteTableAdd,
    current_user: User = Depends(UserManager().get_current_user),
    db_session: Session = Depends(DatabaseManager().get_session),
    note_manager: NoteManager = Depends(NoteManager),
):
    return await note_manager.add_note(body_of_note, current_user, db_session)


@note_router.patch("/update_note/{note_id}")
def update_note(note_id: int):
    return {"Hello world from note.py -> Update note": note_id}


@note_router.delete("/delete_note/{note_id}")
def delete_note(note_id: int):
    return {"Hello world from note.py -> Delete note": note_id}


@note_router.get("/show_notes")
def show_notes():
    return {"Hello world": "from note.py -> show notes"}


@note_router.get("/show_note/{note_id}")
def show_note(note_id: int):
    return {"Hello world from note.py -> show note: note id:": note_id}
