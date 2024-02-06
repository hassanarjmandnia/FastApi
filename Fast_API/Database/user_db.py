from .database import GeneralDatabaseAction
from .models import User
from datetime import datetime

class UserDatabaseAction(GeneralDatabaseAction):

    def __init__(self):
        super().__init__()

    def get_user_by_id(self, user_id, db_session):
        return db_session.query(User).get(user_id)

    def get_user_by_email(self, email, db_session):
        return db_session.query(User).filter(User.email == email).first()

    def add_user(self, user, db_session):
        self.add_item(user, db_session)
        self.commit_changes(db_session)
        self.refresh_item(user, db_session)
        return user

    def update_last_password_change(self, user, db_session):
        user.last_password_change = datetime.now
        self.commit_changes(db_session)
        self.refresh_item(user, db_session)
        return user
