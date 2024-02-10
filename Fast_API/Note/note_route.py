from .note_schemas import NoteTableAdd, NoteTableResponse
from Fast_API.Database.database import DatabaseManager
from Fast_API.User.user_modules import UserManager
from Fast_API.utils.logger import loggers
from Fast_API.Database.models import User
from fastapi import APIRouter, Depends
from .note_modules import NoteManager
from sqlalchemy.orm import Session

note_router = APIRouter()


@note_router.get("/show_all", response_model=list[NoteTableResponse])
async def show_notes(
    current_user: User = Depends(UserManager().get_current_user),
    db_session: Session = Depends(DatabaseManager().get_session),
    note_manager: NoteManager = Depends(NoteManager),
):
    return await note_manager.show_notes(db_session)


@note_router.get("/show/{note_id}", response_model=NoteTableResponse)
async def show_notes(
    note_id: int,
    current_user: User = Depends(UserManager().get_current_user),
    db_session: Session = Depends(DatabaseManager().get_session),
    note_manager: NoteManager = Depends(NoteManager),
):
    return await note_manager.show_note(note_id, db_session)


@note_router.post("/add", response_model=NoteTableResponse)
async def add_note(
    body_of_note: NoteTableAdd,
    current_user: User = Depends(UserManager().get_current_user),
    db_session: Session = Depends(DatabaseManager().get_session),
    note_manager: NoteManager = Depends(NoteManager),
):
    return await note_manager.add_note(body_of_note, current_user, db_session)


@note_router.patch("/update/{note_id}", response_model=NoteTableResponse)
async def update_note(
    note_id: int,
    body_of_note: NoteTableAdd,
    current_user: User = Depends(UserManager().get_current_user),
    db_session: Session = Depends(DatabaseManager().get_session),
    note_manager: NoteManager = Depends(NoteManager),
):
    return await note_manager.update_note(
        current_user, note_id, body_of_note, db_session
    )


@note_router.delete("/delete/{note_id}")
async def delete_note(
    note_id: int,
    current_user: User = Depends(UserManager().get_current_user),
    db_session: Session = Depends(DatabaseManager().get_session),
    note_manager: NoteManager = Depends(NoteManager),
):
    return await note_manager.delete_note(current_user, note_id, db_session)
