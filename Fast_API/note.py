from .schemas import NoteTableAdd
from .auth import oauth_2_schemes, AuthManager
from fastapi import APIRouter, Depends
from .logger import loggers


note_router = APIRouter()


@note_router.get("/test")
def test():
    return {"Hello world": "from note.py"}


@note_router.get("/show_notes")
def show_notes():
    return {"Hello world": "from note.py -> show notes"}


@note_router.get("/show_note/{note_id}")
def show_note(note_id: int):
    return {"Hello world from note.py -> show note: note id:": note_id}


@note_router.post("/add_note")
def add_note(body_of_note: NoteTableAdd):
    return {"Hello world from note.py -> Add note": body_of_note}


@note_router.patch("/update_note/{note_id}")
def update_note(note_id: int):
    return {"Hello world from note.py -> Update note": note_id}


@note_router.delete("/delete_note/{note_id}")
def delete_note(note_id: int):
    return {"Hello world from note.py -> Delete note": note_id}
