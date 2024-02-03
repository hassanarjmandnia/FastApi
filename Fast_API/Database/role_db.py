from .database import GeneralDatabaseAction
from .models import Role


class RoleDatabaseAction(GeneralDatabaseAction):

    def __init__(self, db):
        super().__init__(db)

    def get_role_by_name(self, role_name):
        return self.db.query(Role).filter(Role.name == role_name).first()

    def add_role(self, role):
        self.add_item(role)
        self.commit_changes()
        self.refresh_item(role)
        return role
