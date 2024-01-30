from .schemas import NoteTableAdd
from .auth import oauth_2_schemes, AuthManager
from fastapi import APIRouter, Depends
from .logger import loggers
from .user import UserManager

note_router = APIRouter()


@note_router.get("/show_notes")
def show_notes():
    return {"Hello world": "from note.py -> show notes"}


@note_router.get("/show_note/{note_id}")
def show_note(note_id: int):
    return {"Hello world from note.py -> show note: note id:": note_id}


@note_router.post("/add_note")
async def add_note(
    current_user: dict = Depends(UserManager().find_user_info),
):
    return {"message": "Note added successfully", "user_info": current_user}


@note_router.post("/addd_note")
async def add_note(
    body_of_note: NoteTableAdd,
    token: str = Depends(oauth_2_schemes),
    user_manager: UserManager = Depends(UserManager),
):
    user = await user_manager.find_user_info(token)
    if user:
        return {"Hello world from note.py -> Add note": body_of_note}
    else:
        return {"Bye world from note.py -> Add note": body_of_note}


@note_router.patch("/update_note/{note_id}")
def update_note(note_id: int):
    return {"Hello world from note.py -> Update note": note_id}


@note_router.delete("/delete_note/{note_id}")
def delete_note(note_id: int):
    return {"Hello world from note.py -> Delete note": note_id}
