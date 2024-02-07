from Fast_API.Database.database import DatabaseManager
from .note_schemas import NoteTableAdd
from Fast_API.Auth.auth import oauth_2_schemes, AuthManager
from fastapi import APIRouter, Depends
from Fast_API.utils.logger import loggers
from Fast_API.User.user_route import UserManager
from sqlalchemy.orm import Session

note_router = APIRouter()


@note_router.post("/add_note")
async def add_note(
    body_of_note: NoteTableAdd,
    db_session: Session = Depends(DatabaseManager().get_session),
    user_manager: UserManager = Depends(UserManager),
    token: str = Depends(oauth_2_schemes),
):
    user = await user_manager.find_user_info(token, db_session)
    if user:
        return {"Hello world from note.py -> Add note": user}
    else:
        return {"Bye world from note.py -> Add note": body_of_note}


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
