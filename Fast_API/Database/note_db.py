from .database import GeneralDatabaseAction
from .models import Note


class NoteDatabaseAction(GeneralDatabaseAction):

    def __init__(self):
        super().__init__()

    def get_user_by_id(self, user_id, db_session):
        pass
        # return db_session.query(User).get(user_id)

    def get_user_by_email(self, email, db_session):
        pass
        # return db_session.query(User).filter(User.email == email).first()

    def add_note(self, note, db_session):
        self.add_item(note, db_session)
        self.commit_changes(db_session)
        self.refresh_item(note, db_session)
        return note
