from .superadmin_schemas import RoleTableAdd
from Fast_API.Database.models import Role, User
from sqlalchemy.orm import Session
from Fast_API.Database.role_db import RoleDatabaseAction
from fastapi.responses import JSONResponse


class SuperAdminAction:
    def __init__(self, role_database_action):
        self.role_database_action = role_database_action

    def add_role(self, role_name, db_session):
        existing_role = self.role_database_action.get_role_by_name(
            role_name.name, db_session
        )
        if existing_role:
            message = "Role already exists. Please choose a different role name"
            status_code = 409
            return JSONResponse(content={"message": message}, status_code=status_code)
        else:
            new_role = Role(**role_name.model_dump())
            new_role = self.role_database_action.add_role(new_role, db_session)
            message = "New Role Add Successfully"
            status_code = 200
            return JSONResponse(content={"message": message}, status_code=status_code)


class SuperAdminManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.role_database_action = RoleDatabaseAction()
            cls._instance.worker = SuperAdminAction(cls._instance.role_database_action)
        return cls._instance

    def add_role(self, role_name: RoleTableAdd, db_session: Session):
        return self.worker.add_role(role_name, db_session)
