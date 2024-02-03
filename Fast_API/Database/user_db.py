from .database import GeneralDatabaseAction
from .models import User


class UserDatabaseAction(GeneralDatabaseAction):

    def __init__(self, db):
        super().__init__(db)

    def get_user_by_id(self, user_id):
        return self.db.query(User).get(user_id)

    def get_user_by_email(self, email):
        return self.db.query(User).filter(User.email == email).first()

    def add_user(self, user):
        self.add_item(user)
        self.commit_changes()
        self.refresh_item(user)
        return user
