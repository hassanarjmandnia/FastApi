from Fast_API.Database.models import User
from Fast_API.Note.note_schemas import NoteTableAdd


class NoteAction:
    def __init__(self):
        pass

    async def add_note(self, body_of_note: NoteTableAdd, user: User):
        return {
            "Add Note Function Recive this note": body_of_note,
            "And This User": user,
        }


class NoteManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.worker = NoteAction()
        return cls._instance

    async def add_note(self, body_of_note: NoteTableAdd, user: User):
        return await self.worker.add_note(body_of_note, user)
