from .database import GeneralDatabaseAction
from .models import Role


class RoleDatabaseAction(GeneralDatabaseAction):

    def __init__(self):
        super().__init__()

    def get_role_by_name(self, role_name, db_session):
        return db_session.query(Role).filter(Role.name == role_name).first()

    def add_role(self, role, db_session):
        self.add_item(role, db_session)
        self.commit_changes(db_session)
        self.refresh_item(role, db_session)
        return role
