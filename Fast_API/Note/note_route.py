from Fast_API.Database.database import DatabaseManager
from .note_schemas import NoteTableAdd
from Fast_API.Auth.auth import oauth_2_schemes, AuthManager
from fastapi import APIRouter, Depends
from Fast_API.utils.logger import loggers
from Fast_API.User.user_modules import UserManager
from sqlalchemy.orm import Session
from Fast_API.Database.models import User

note_router = APIRouter()


"""@note_router.post("/add_note")
async def add_note(
    body_of_note: NoteTableAdd,
    user_info: User = Depends(UserManager().get_user_from_token),
):
    # do something with resullt of get user from token function! maybe something like this:
    # note_manager = note_manager()
    # note_manager.add_note(body_of_note,user_info)
    # for now, we just simply what it give us
    return user_info"""


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
