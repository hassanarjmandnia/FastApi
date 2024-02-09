from .database import GeneralDatabaseAction
from .models import Note


class NoteDatabaseAction(GeneralDatabaseAction):

    def __init__(self):
        super().__init__()

    def get_all_of_notes(self, db_session):
        notes = db_session.query(Note).all()
        return notes

    def get_note_by_id(self, note_id, db_session):
        return db_session.query(Note).get(note_id)

    def add_note(self, note, db_session):
        self.add_item(note, db_session)
        self.commit_changes(db_session)
        self.refresh_item(note, db_session)
        return note
