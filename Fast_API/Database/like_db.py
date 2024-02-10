from .database import GeneralDatabaseAction
from .models import Like


class LikeDatabaseAction(GeneralDatabaseAction):

    def __init__(self):
        super().__init__()

    def add_like(self, like, db_session):
        self.add_item(like, db_session)
        self.commit_changes(db_session)
        self.refresh_item(like, db_session)
        return like

    def delete_like(self, like, db_session):
        self.delete_item(like, db_session)
        self.commit_changes(db_session)

    def get_existing_like(self, user_id, note_id, db_session):
        return (
            db_session.query(Like)
            .filter(Like.user_id == user_id, Like.note_id == note_id)
            .first()
        )

    def get_all_likes_of_a_note(self, note_id, db_session):
        return db_session.query(Like).filter(Like.note_id == note_id).all()

    def get_all_likes_from_a_user(self, user_id, db_session):
        return db_session.query(Like).filter(Like.user_id == user_id).all()
